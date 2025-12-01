"""
ROBO Tests - Unit tests for trading strategies
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategies.ROBO_rsi_strategy import ROBORSIStrategy
from strategies.ROBO_ema_strategy import ROBOEMAStrategy
from utils.ROBO_validators import DataValidator, ConfigValidator
from utils.ROBO_data_loader import ROBODataLoader


class TestDataValidator:
    """Test data validation"""
    
    def test_valid_ohlcv(self):
        """Test validation of valid OHLCV data"""
        df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2024-01-01', periods=3, freq='15min'))
        
        validator = DataValidator()
        assert validator.validate_ohlcv(df, "TEST") == True
    
    def test_invalid_high_low(self):
        """Test validation fails when High < Low"""
        df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [95, 96, 97],  # High < Low - invalid
            'Low': [105, 106, 107],
            'Close': [103, 104, 105],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2024-01-01', periods=3, freq='15min'))
        
        validator = DataValidator()
        assert validator.validate_ohlcv(df, "TEST") == False
    
    def test_nan_values(self):
        """Test validation fails with NaN values"""
        df = pd.DataFrame({
            'Open': [100, np.nan, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2024-01-01', periods=3, freq='15min'))
        
        validator = DataValidator()
        assert validator.validate_ohlcv(df, "TEST") == False


class TestConfigValidator:
    """Test configuration validation"""
    
    def test_valid_config(self):
        """Test validation of valid config"""
        config = {
            'strategy': {'name': 'Test'},
            'trade_direction': 'long',
            'indicators': {},
            'risk_management': {
                'risk_per_trade_percent': 2.0,
                'max_position_size_percent': 95.0
            },
            'backtest': {}
        }
        
        validator = ConfigValidator()
        assert validator.validate_strategy_config(config) == True
    
    def test_invalid_trade_direction(self):
        """Test validation fails with invalid trade direction"""
        config = {
            'strategy': {'name': 'Test'},
            'trade_direction': 'invalid',  # Invalid
            'indicators': {},
            'risk_management': {
                'risk_per_trade_percent': 2.0,
                'max_position_size_percent': 95.0
            },
            'backtest': {}
        }
        
        validator = ConfigValidator()
        assert validator.validate_strategy_config(config) == False
    
    def test_missing_section(self):
        """Test validation fails with missing section"""
        config = {
            'strategy': {'name': 'Test'},
            'trade_direction': 'long',
            # Missing 'indicators', 'risk_management', 'backtest'
        }
        
        validator = ConfigValidator()
        assert validator.validate_strategy_config(config) == False


class TestRSIStrategy:
    """Test RSI strategy logic"""
    
    def test_strategy_parameters(self):
        """Test that strategy parameters can be set"""
        ROBORSIStrategy.RSI_PERIOD = 14
        ROBORSIStrategy.RSI_OVERSOLD = 30
        ROBORSIStrategy.RSI_OVERBOUGHT = 70
        
        assert ROBORSIStrategy.RSI_PERIOD == 14
        assert ROBORSIStrategy.RSI_OVERSOLD == 30
        assert ROBORSIStrategy.RSI_OVERBOUGHT == 70


class TestEMAStrategy:
    """Test EMA strategy logic"""
    
    def test_strategy_parameters(self):
        """Test that strategy parameters can be set"""
        ROBOEMAStrategy.EMA_FAST = 9
        ROBOEMAStrategy.EMA_SLOW = 50
        ROBOEMAStrategy.SMA_TREND = 100
        
        assert ROBOEMAStrategy.EMA_FAST == 9
        assert ROBOEMAStrategy.EMA_SLOW == 50
        assert ROBOEMAStrategy.SMA_TREND == 100


def test_sample_data_generation():
    """Test that we can generate sample data for testing"""
    dates = pd.date_range('2024-01-01', periods=500, freq='15min')
    
    # Generate realistic OHLCV data
    close_prices = 100 + np.cumsum(np.random.randn(500) * 2)
    
    df = pd.DataFrame({
        'Open': close_prices + np.random.randn(500) * 0.5,
        'High': close_prices + abs(np.random.randn(500) * 2),
        'Low': close_prices - abs(np.random.randn(500) * 2),
        'Close': close_prices,
        'Volume': np.random.randint(1000, 10000, 500)
    }, index=dates)
    
    # Ensure OHLC relationships are valid
    df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
    df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
    
    validator = DataValidator()
    assert validator.validate_ohlcv(df, "SAMPLE") == True
    assert len(df) == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
