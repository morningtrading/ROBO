"""
ROBO Data Loader - Handles loading and preprocessing of market data
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from .ROBO_logger import get_logger
from .ROBO_validators import DataValidator

logger = get_logger()


class ROBODataLoader:
    """Load and preprocess market data"""
    
    def __init__(self, data_dir: str):
        """
        Initialize data loader
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.validator = DataValidator()
        
        if not self.data_dir.exists():
            logger.error(f"Data directory does not exist: {self.data_dir}")
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
    
    def load_coin_data(self, filename: str, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load and validate data for a single coin
        
        Args:
            filename: CSV filename
            symbol: Trading symbol
            
        Returns:
            DataFrame or None if loading fails
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.error(f"{symbol}: File not found: {filepath}")
            return None
        
        try:
            logger.info(f"{symbol}: Loading data from {filename}")
            
            # Load CSV
            df = pd.read_csv(filepath)
            
            # Handle different date column formats
            date_col = 'date' if 'date' in df.columns else 'Datetime'
            if date_col not in df.columns:
                logger.error(f"{symbol}: No date column found")
                return None
            
            # Clean timestamp (remove timezone if present)
            if df[date_col].dtype == 'object':
                df[date_col] = df[date_col].str.replace(r'\+00:00$', '', regex=True)
            
            # Rename columns to standard format
            column_mapping = {
                'date': 'Datetime',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Convert to datetime and set as index
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df.set_index('Datetime')
            
            # Select and convert OHLCV columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
            
            # Sort by time
            df = df.sort_index()
            
            # Remove duplicates
            df = df[~df.index.duplicated(keep='first')]
            
            # Validate data
            if not self.validator.validate_ohlcv(df, symbol):
                logger.error(f"{symbol}: Data validation failed")
                return None
            
            logger.info(f"{symbol}: Successfully loaded {len(df)} bars")
            return df
            
        except Exception as e:
            logger.error(f"{symbol}: Error loading data: {e}")
            return None
    
    def load_all_coins(self, coins_config: list) -> Dict[str, pd.DataFrame]:
        """
        Load data for all configured coins
        
        Args:
            coins_config: List of coin configurations
            
        Returns:
            Dictionary of symbol -> DataFrame
        """
        data = {}
        
        for coin in coins_config:
            if not coin.get('enabled', True):
                logger.info(f"{coin['symbol']}: Skipped (disabled in config)")
                continue
            
            df = self.load_coin_data(coin['filename'], coin['symbol'])
            if df is not None:
                data[coin['symbol']] = df
            else:
                logger.warning(f"{coin['symbol']}: Failed to load, skipping")
        
        logger.info(f"Successfully loaded {len(data)} out of {len(coins_config)} coins")
        return data
