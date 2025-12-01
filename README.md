# ROBO
Crypto robot test and experimentation - not for real

A parameter sweeping bot that tests various trading strategies across multiple cryptocurrencies.

## Features

- **Multiple Trading Strategies**: SMA Crossover, RSI, MACD, Bollinger Bands
- **Parameter Sweeping**: Automatically tests different parameter combinations
- **Multiple Cryptocurrencies**: Supports Bitcoin, Ethereum, Binance Coin, Solana, Cardano
- **Backtesting Engine**: Simulates trading with realistic commission costs
- **Performance Metrics**: Total return, Sharpe ratio, win rate, max drawdown
- **Visualization**: Generates comparison charts and performance plots

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run a quick demo:
```bash
python demo.py
```

Run a full parameter sweep:
```bash
python sweep.py
```

## Usage

### Basic Usage

```bash
# Test all strategies on all default cryptocurrencies
python sweep.py

# Test specific strategies
python sweep.py --strategies sma_crossover rsi

# Test specific cryptocurrencies
python sweep.py --cryptos BTC-USD ETH-USD

# Use different time period
python sweep.py --period 2y --interval 1d

# Save results to custom file
python sweep.py --output my_results.csv
```

### Advanced Options

```bash
python sweep.py --help
```

Options include:
- `--strategies`: Which strategies to test (sma_crossover, rsi, macd, bollinger_bands)
- `--cryptos`: Which cryptocurrencies to test
- `--period`: Historical data period (e.g., 1y, 6mo, 2y)
- `--interval`: Data interval (e.g., 1d, 1h)
- `--capital`: Initial capital for backtesting (default: 10000)
- `--commission`: Commission rate per trade (default: 0.001)
- `--output`: Output CSV filename
- `--no-plots`: Skip generating visualization plots

## Output

The sweeper generates:
1. **Console Report**: Summary statistics and top performing configurations
2. **CSV File**: Detailed results for all tested combinations (`results.csv`)
3. **Visualizations**: 
   - `strategy_comparison.png`: Comparison of strategies across metrics
   - `top_strategies.png`: Top 15 best performing configurations

## Strategies

### 1. SMA Crossover
Simple Moving Average crossover strategy. Buys when short MA crosses above long MA.

Parameters:
- `short_window`: Short moving average period
- `long_window`: Long moving average period

### 2. RSI (Relative Strength Index)
Momentum oscillator strategy. Buys when oversold, sells when overbought.

Parameters:
- `period`: RSI calculation period
- `oversold`: Oversold threshold
- `overbought`: Overbought threshold

### 3. MACD
Moving Average Convergence Divergence strategy.

Parameters:
- `fast_period`: Fast EMA period
- `slow_period`: Slow EMA period
- `signal_period`: Signal line period

### 4. Bollinger Bands
Volatility-based strategy using standard deviation bands.

Parameters:
- `period`: Moving average period
- `std_dev`: Standard deviation multiplier

## Customization

Edit `robo/config.py` to customize:
- Cryptocurrencies to test
- Parameter ranges for each strategy
- Backtesting configuration

## Disclaimer

**This is for testing and experimentation only. Not for real trading.**

The backtesting results do not guarantee future performance. Past performance is not indicative of future results. Use at your own risk.
