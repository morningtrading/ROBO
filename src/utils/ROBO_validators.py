"""
ROBO Validators - Data validation utilities
"""

import pandas as pd
import numpy as np
from .ROBO_logger import get_logger

logger = get_logger()


class DataValidator:
    """Validates OHLCV data integrity"""
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame, symbol: str = "Unknown") -> bool:
        """
        Validate OHLCV dataframe
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Symbol name for logging
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                logger.error(f"{symbol}: Missing columns: {missing}")
                return False
            
            # Check for NaN values
            if df[required_cols].isnull().any().any():
                nan_counts = df[required_cols].isnull().sum()
                logger.warning(f"{symbol}: NaN values found: {nan_counts.to_dict()}")
                return False
            
            # Check OHLC relationships
            if not (df['High'] >= df['Low']).all():
                logger.error(f"{symbol}: High < Low detected")
                return False
            
            if not (df['High'] >= df['Open']).all():
                logger.error(f"{symbol}: High < Open detected")
                return False
            
            if not (df['High'] >= df['Close']).all():
                logger.error(f"{symbol}: High < Close detected")
                return False
            
            if not (df['Low'] <= df['Open']).all():
                logger.error(f"{symbol}: Low > Open detected")
                return False
            
            if not (df['Low'] <= df['Close']).all():
                logger.error(f"{symbol}: Low > Close detected")
                return False
            
            # Check for negative values
            if (df[required_cols] < 0).any().any():
                logger.error(f"{symbol}: Negative values detected")
                return False
            
            # Check for zero volume
            zero_volume = (df['Volume'] == 0).sum()
            if zero_volume > 0:
                logger.warning(f"{symbol}: {zero_volume} bars with zero volume")
            
            # Check data is sorted
            if not df.index.is_monotonic_increasing:
                logger.warning(f"{symbol}: Data is not sorted by time")
                return False
            
            logger.info(f"{symbol}: Validation passed ({len(df)} bars)")
            return True
            
        except Exception as e:
            logger.error(f"{symbol}: Validation error: {e}")
            return False
    
    @staticmethod
    def check_data_gaps(df: pd.DataFrame, expected_freq: str, symbol: str = "Unknown") -> list:
        """
        Check for gaps in time series data
        
        Args:
            df: DataFrame with DatetimeIndex
            expected_freq: Expected frequency (e.g., '15min')
            symbol: Symbol name
            
        Returns:
            list: List of gap periods
        """
        gaps = []
        expected_diff = pd.Timedelta(expected_freq)
        
        time_diffs = df.index.to_series().diff()
        gap_mask = time_diffs > expected_diff * 1.5
        
        if gap_mask.any():
            gap_indices = df.index[gap_mask]
            for idx in gap_indices:
                gaps.append({
                    'timestamp': idx,
                    'gap_size': time_diffs[idx]
                })
            logger.warning(f"{symbol}: Found {len(gaps)} data gaps")
        
        return gaps


class ConfigValidator:
    """Validates configuration files"""
    
    @staticmethod
    def validate_strategy_config(config: dict) -> bool:
        """
        Validate strategy configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if valid
        """
        try:
            # Check required sections
            required = ['strategy', 'trade_direction', 'indicators', 
                       'risk_management', 'backtest']
            for section in required:
                if section not in config:
                    logger.error(f"Missing config section: {section}")
                    return False
            
            # Validate trade direction
            valid_directions = ['long', 'short', 'both']
            if config['trade_direction'] not in valid_directions:
                logger.error(f"Invalid trade_direction. Must be one of: {valid_directions}")
                return False
            
            # Validate risk parameters
            risk = config['risk_management']
            if risk['risk_per_trade_percent'] <= 0 or risk['risk_per_trade_percent'] > 100:
                logger.error("risk_per_trade_percent must be between 0 and 100")
                return False
            
            if risk['max_position_size_percent'] <= 0 or risk['max_position_size_percent'] > 100:
                logger.error("max_position_size_percent must be between 0 and 100")
                return False
            
            logger.info("Strategy config validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False
