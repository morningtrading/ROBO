"""
Data fetcher for cryptocurrency historical prices.
"""

import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime


class DataFetcher:
    """Fetches historical cryptocurrency price data."""
    
    def __init__(self):
        self.cache = {}
    
    def fetch(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTC-USD')
            period: Time period (e.g., '1y', '6mo', '1mo')
            interval: Data interval (e.g., '1d', '1h')
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        cache_key = f"{symbol}_{period}_{interval}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"Warning: No data retrieved for {symbol}")
                return None
            
            # Ensure we have the required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                print(f"Warning: Missing required columns for {symbol}")
                return None
            
            self.cache[cache_key] = data
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_multiple(self, symbols: list, period: str = "1y", interval: str = "1d") -> dict:
        """
        Fetch historical data for multiple cryptocurrencies.
        
        Args:
            symbols: List of cryptocurrency symbols
            period: Time period
            interval: Data interval
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        for symbol in symbols:
            print(f"Fetching data for {symbol}...")
            data = self.fetch(symbol, period, interval)
            if data is not None:
                results[symbol] = data
        return results
