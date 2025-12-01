"""
Configuration for crypto bot parameter sweeping.
"""

# Major cryptocurrencies to test
CRYPTOCURRENCIES = [
    "BTC-USD",   # Bitcoin
    "ETH-USD",   # Ethereum
    "BNB-USD",   # Binance Coin
    "SOL-USD",   # Solana
    "ADA-USD",   # Cardano
]

# Default parameter ranges for strategy sweeping
STRATEGY_PARAMS = {
    "sma_crossover": {
        "short_window": [5, 10, 20, 30],
        "long_window": [50, 100, 200],
    },
    "rsi": {
        "period": [7, 14, 21, 28],
        "oversold": [20, 25, 30],
        "overbought": [70, 75, 80],
    },
    "macd": {
        "fast_period": [8, 12, 16],
        "slow_period": [21, 26, 30],
        "signal_period": [7, 9, 11],
    },
    "bollinger_bands": {
        "period": [10, 20, 30],
        "std_dev": [1.5, 2.0, 2.5, 3.0],
    },
}

# Backtesting settings
BACKTEST_CONFIG = {
    "initial_capital": 10000.0,
    "commission": 0.001,  # 0.1% per trade
    "data_period": "1y",  # 1 year of historical data
    "data_interval": "1d",  # Daily data
}
