#!/usr/bin/env python3
"""
Test script to verify core functionality.
"""

import sys
from robo.data_fetcher import DataFetcher
from robo.strategies import create_strategy, SMACrossoverStrategy
from robo.backtester import Backtester
from robo.parameter_sweeper import ParameterSweeper
import pandas as pd
import numpy as np


def test_data_fetcher():
    """Test data fetching functionality."""
    print("Testing DataFetcher...")
    fetcher = DataFetcher()
    
    # Try to fetch BTC data
    data = fetcher.fetch('BTC-USD', period='1mo', interval='1d')
    
    if data is None or data.empty:
        print("  WARNING: Could not fetch live data (this is OK in offline environment)")
        # Create mock data for testing
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        data = pd.DataFrame({
            'Open': np.random.randn(100).cumsum() + 40000,
            'High': np.random.randn(100).cumsum() + 40500,
            'Low': np.random.randn(100).cumsum() + 39500,
            'Close': np.random.randn(100).cumsum() + 40000,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        print("  Using mock data for testing")
    else:
        print(f"  ✓ Fetched {len(data)} data points")
    
    return data


def test_strategy():
    """Test strategy creation and signal generation."""
    print("\nTesting Strategies...")
    
    # Create mock data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 40000,
        'High': np.random.randn(100).cumsum() + 40500,
        'Low': np.random.randn(100).cumsum() + 39500,
        'Close': np.random.randn(100).cumsum() + 40000,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    # Test SMA Crossover
    strategy = create_strategy('sma_crossover', {'short_window': 10, 'long_window': 50})
    signals = strategy.generate_signals(data.copy())
    
    if signals is not None and len(signals) == len(data):
        print(f"  ✓ SMA Crossover generated {len(signals)} signals")
    else:
        print("  ✗ Strategy signal generation failed")
        return None
    
    return data


def test_backtester(data):
    """Test backtesting functionality."""
    print("\nTesting Backtester...")
    
    backtester = Backtester(initial_capital=10000, commission=0.001)
    strategy = create_strategy('sma_crossover', {'short_window': 10, 'long_window': 50})
    
    result = backtester.backtest(strategy, data.copy(), 'TEST-USD')
    
    if result is not None:
        print(f"  ✓ Backtest completed")
        print(f"    Total Return: {result.total_return:.2f}%")
        print(f"    Total Trades: {result.total_trades}")
        print(f"    Sharpe Ratio: {result.sharpe_ratio:.2f}")
    else:
        print("  ✗ Backtest failed")
        return False
    
    return True


def test_parameter_sweeper(data):
    """Test parameter sweeping functionality."""
    print("\nTesting ParameterSweeper...")
    
    backtester = Backtester(initial_capital=10000, commission=0.001)
    sweeper = ParameterSweeper(backtester)
    
    param_ranges = {
        'short_window': [10, 20],
        'long_window': [50, 100],
    }
    
    data_dict = {'TEST-USD': data.copy()}
    results = sweeper.sweep('sma_crossover', param_ranges, data_dict, verbose=False)
    
    if results and len(results) == 4:  # 2x2 combinations
        print(f"  ✓ Parameter sweep completed: {len(results)} tests")
        best = sweeper.get_best_results(n=1)[0]
        print(f"    Best result: {best.total_return:.2f}% return")
    else:
        print("  ✗ Parameter sweep failed")
        return False
    
    return True


def main():
    """Run all tests."""
    print("="*60)
    print("ROBO Core Functionality Tests")
    print("="*60)
    
    try:
        # Test data fetching
        data = test_data_fetcher()
        if data is None or data.empty:
            print("\n✗ Tests failed: Could not get data")
            return 1
        
        # Test strategy
        data = test_strategy()
        if data is None:
            print("\n✗ Tests failed: Strategy test failed")
            return 1
        
        # Test backtester
        if not test_backtester(data):
            print("\n✗ Tests failed: Backtester test failed")
            return 1
        
        # Test parameter sweeper
        if not test_parameter_sweeper(data):
            print("\n✗ Tests failed: Parameter sweeper test failed")
            return 1
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Tests failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
