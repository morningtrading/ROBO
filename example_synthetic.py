#!/usr/bin/env python3
"""
Example demonstrating the parameter sweeper with synthetic data.
This shows how the bot works without requiring internet access.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from robo.backtester import Backtester
from robo.parameter_sweeper import ParameterSweeper
from robo.visualization import print_summary_report, save_results_to_csv


def generate_synthetic_crypto_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """
    Generate synthetic cryptocurrency price data with realistic characteristics.
    
    Args:
        symbol: Cryptocurrency symbol
        days: Number of days of data to generate
        
    Returns:
        DataFrame with OHLCV data
    """
    np.random.seed(hash(symbol) % 2**32)  # Different seed per symbol
    
    # Start date
    start_date = datetime.now() - timedelta(days=days)
    dates = pd.date_range(start=start_date, periods=days, freq='D')
    
    # Generate base price with trend and volatility
    base_price = 40000 if 'BTC' in symbol else (2500 if 'ETH' in symbol else 
                 (400 if 'BNB' in symbol else (100 if 'SOL' in symbol else 0.5)))
    
    # Random walk with drift
    returns = np.random.normal(0.001, 0.02, days)  # Mean 0.1% daily, 2% volatility
    price_series = base_price * (1 + returns).cumprod()
    
    # Add some trends and volatility
    trend = np.linspace(0, 0.3, days)  # 30% uptrend over the period
    price_series = price_series * (1 + trend)
    
    # Generate OHLCV data
    data = pd.DataFrame(index=dates)
    data['Close'] = price_series
    data['Open'] = price_series * (1 + np.random.normal(0, 0.005, days))
    data['High'] = np.maximum(data['Open'], data['Close']) * (1 + np.abs(np.random.normal(0, 0.01, days)))
    data['Low'] = np.minimum(data['Open'], data['Close']) * (1 - np.abs(np.random.normal(0, 0.01, days)))
    data['Volume'] = np.random.lognormal(15, 1, days)
    
    return data


def main():
    print("="*80)
    print("ROBO - Synthetic Data Example")
    print("Demonstrating parameter sweep with generated cryptocurrency data")
    print("="*80)
    
    # Generate synthetic data for multiple cryptocurrencies
    cryptos = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'ADA-USD']
    
    print("\nGenerating synthetic data...")
    data_dict = {}
    for crypto in cryptos:
        data = generate_synthetic_crypto_data(crypto, days=365)
        data_dict[crypto] = data
        print(f"  {crypto}: {len(data)} days from {data.index[0].date()} to {data.index[-1].date()}")
        print(f"    Price range: ${data['Low'].min():.2f} - ${data['High'].max():.2f}")
    
    # Setup backtester and sweeper
    print("\n" + "="*80)
    print("Running Parameter Sweep")
    print("="*80)
    
    backtester = Backtester(initial_capital=10000.0, commission=0.001)
    sweeper = ParameterSweeper(backtester)
    
    # Test SMA Crossover strategy
    print("\n1. Testing SMA Crossover Strategy...")
    sma_params = {
        'short_window': [10, 20, 30],
        'long_window': [50, 100, 200],
    }
    sweeper.sweep('sma_crossover', sma_params, data_dict, verbose=True)
    
    # Test RSI strategy
    print("\n2. Testing RSI Strategy...")
    rsi_params = {
        'period': [14, 21],
        'oversold': [25, 30],
        'overbought': [70, 75],
    }
    sweeper.sweep('rsi', rsi_params, data_dict, verbose=True)
    
    # Test MACD strategy
    print("\n3. Testing MACD Strategy...")
    macd_params = {
        'fast_period': [12, 16],
        'slow_period': [26, 30],
        'signal_period': [9, 11],
    }
    sweeper.sweep('macd', macd_params, data_dict, verbose=True)
    
    # Test Bollinger Bands strategy
    print("\n4. Testing Bollinger Bands Strategy...")
    bb_params = {
        'period': [20, 30],
        'std_dev': [2.0, 2.5],
    }
    sweeper.sweep('bollinger_bands', bb_params, data_dict, verbose=True)
    
    # Generate reports
    print("\n" + "="*80)
    print("Results Summary")
    print("="*80)
    
    print_summary_report(sweeper)
    
    # Save results
    save_results_to_csv(sweeper, 'synthetic_results.csv')
    
    # Show best configurations per strategy
    print("\n" + "="*80)
    print("BEST CONFIGURATION PER STRATEGY")
    print("="*80)
    
    df = sweeper.results_to_dataframe()
    for strategy in df['strategy'].unique():
        strategy_df = df[df['strategy'] == strategy]
        best = strategy_df.nlargest(1, 'total_return').iloc[0]
        print(f"\n{strategy}:")
        print(f"  Parameters: {best['params']}")
        print(f"  Best Symbol: {best['symbol']}")
        print(f"  Total Return: {best['total_return']:.2f}%")
        print(f"  Sharpe Ratio: {best['sharpe_ratio']:.2f}")
        print(f"  Win Rate: {best['win_rate']:.2f}%")
    
    print("\n" + "="*80)
    print("Example Complete!")
    print("="*80)
    print("\nResults saved to 'synthetic_results.csv'")
    print("This demonstrates how the parameter sweeper works.")
    print("With real data (internet connection), use: python sweep.py")


if __name__ == '__main__':
    main()
