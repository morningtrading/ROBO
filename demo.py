#!/usr/bin/env python3
"""
Quick demo of the ROBO parameter sweeper.
Tests a single strategy on a couple of cryptocurrencies.
"""

from robo.config import BACKTEST_CONFIG
from robo.data_fetcher import DataFetcher
from robo.backtester import Backtester
from robo.parameter_sweeper import ParameterSweeper
from robo.visualization import print_summary_report


def main():
    print("ROBO Quick Demo - Testing SMA Crossover Strategy")
    print("="*60)
    
    # Fetch data for Bitcoin and Ethereum
    print("\nFetching data...")
    fetcher = DataFetcher()
    data_dict = fetcher.fetch_multiple(
        ['BTC-USD', 'ETH-USD'],
        period='6mo',
        interval='1d'
    )
    
    if not data_dict:
        print("Error fetching data!")
        return
    
    print(f"Fetched data for {len(data_dict)} cryptocurrencies")
    
    # Setup backtester and sweeper
    backtester = Backtester(
        initial_capital=BACKTEST_CONFIG['initial_capital'],
        commission=BACKTEST_CONFIG['commission']
    )
    sweeper = ParameterSweeper(backtester)
    
    # Test SMA crossover with a few parameter combinations
    print("\nTesting SMA Crossover strategy...")
    param_ranges = {
        'short_window': [10, 20],
        'long_window': [50, 100],
    }
    
    sweeper.sweep('sma_crossover', param_ranges, data_dict, verbose=True)
    
    # Print results
    print_summary_report(sweeper)
    
    print("\n" + "="*60)
    print("Demo complete! Run 'python sweep.py' for full parameter sweep.")


if __name__ == '__main__':
    main()
