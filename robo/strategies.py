"""
Base strategy interface and common strategy implementations.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class Strategy(ABC):
    """Base class for trading strategies."""
    
    def __init__(self, params: Dict[str, Any]):
        """
        Initialize strategy with parameters.
        
        Args:
            params: Dictionary of strategy parameters
        """
        self.params = params
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on price data.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 (buy), -1 (sell), 0 (hold)
        """
        pass
    
    @abstractmethod
    def get_param_names(self) -> List[str]:
        """Return list of parameter names used by this strategy."""
        pass
    
    def __str__(self):
        params_str = ", ".join([f"{k}={v}" for k, v in self.params.items()])
        return f"{self.__class__.__name__}({params_str})"


class SMACrossoverStrategy(Strategy):
    """Simple Moving Average Crossover Strategy."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on SMA crossover."""
        short_window = self.params['short_window']
        long_window = self.params['long_window']
        
        # Calculate moving averages
        data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
        data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        
        # Buy when short MA crosses above long MA
        signals[data['SMA_short'] > data['SMA_long']] = 1
        # Sell when short MA crosses below long MA
        signals[data['SMA_short'] < data['SMA_long']] = -1
        
        return signals
    
    def get_param_names(self) -> List[str]:
        return ['short_window', 'long_window']


class RSIStrategy(Strategy):
    """Relative Strength Index Strategy."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on RSI."""
        period = self.params['period']
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[rsi < oversold] = 1  # Buy when oversold
        signals[rsi > overbought] = -1  # Sell when overbought
        
        return signals
    
    def get_param_names(self) -> List[str]:
        return ['period', 'oversold', 'overbought']


class MACDStrategy(Strategy):
    """Moving Average Convergence Divergence Strategy."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on MACD."""
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        signal_period = self.params['signal_period']
        
        # Calculate MACD
        ema_fast = data['Close'].ewm(span=fast_period).mean()
        ema_slow = data['Close'].ewm(span=slow_period).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal_period).mean()
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[macd > signal_line] = 1  # Buy when MACD crosses above signal
        signals[macd < signal_line] = -1  # Sell when MACD crosses below signal
        
        return signals
    
    def get_param_names(self) -> List[str]:
        return ['fast_period', 'slow_period', 'signal_period']


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands Strategy."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on Bollinger Bands."""
        period = self.params['period']
        std_dev = self.params['std_dev']
        
        # Calculate Bollinger Bands
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        # Generate signals
        signals = pd.Series(0, index=data.index)
        signals[data['Close'] < lower_band] = 1  # Buy when price below lower band
        signals[data['Close'] > upper_band] = -1  # Sell when price above upper band
        
        return signals
    
    def get_param_names(self) -> List[str]:
        return ['period', 'std_dev']


# Strategy factory
STRATEGY_CLASSES = {
    'sma_crossover': SMACrossoverStrategy,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'bollinger_bands': BollingerBandsStrategy,
}


def create_strategy(strategy_name: str, params: Dict[str, Any]) -> Strategy:
    """
    Create a strategy instance.
    
    Args:
        strategy_name: Name of the strategy
        params: Strategy parameters
        
    Returns:
        Strategy instance
    """
    if strategy_name not in STRATEGY_CLASSES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    
    return STRATEGY_CLASSES[strategy_name](params)
