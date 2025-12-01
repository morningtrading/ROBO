# ROBO Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/morningtrading/ROBO.git
cd ROBO

# Install dependencies
pip install -r requirements.txt
```

## Quick Examples

### 1. Run the Quick Demo
Tests a simple strategy on 2 cryptocurrencies:
```bash
python demo.py
```

### 2. Run with Synthetic Data (No Internet Required)
See the bot in action with generated data:
```bash
python example_synthetic.py
```

### 3. Run Full Parameter Sweep (Requires Internet)
Sweep all strategies across all cryptocurrencies:
```bash
python sweep.py
```

### 4. Custom Parameter Sweep
Test specific strategies and cryptos:
```bash
# Test only SMA crossover and RSI strategies
python sweep.py --strategies sma_crossover rsi

# Test only Bitcoin and Ethereum
python sweep.py --cryptos BTC-USD ETH-USD

# Use 2 years of data
python sweep.py --period 2y

# Higher initial capital
python sweep.py --capital 100000
```

## Understanding the Output

### Console Report
The bot displays:
- Progress of data fetching
- Progress of parameter sweep
- Top 10 best configurations by return
- Top 5 best configurations by Sharpe ratio
- Summary statistics by strategy
- Summary statistics by cryptocurrency

### CSV Output (results.csv)
Contains detailed results for every test:
- Strategy name and parameters
- Cryptocurrency symbol
- Total return percentage
- Number of trades
- Win rate
- Sharpe ratio
- Maximum drawdown
- Final capital

### Visualization Files
- `strategy_comparison.png`: Compare all strategies across metrics
- `top_strategies.png`: Bar chart of best performing configurations

## Customizing Parameters

Edit `robo/config.py` to customize:

```python
# Add more cryptocurrencies
CRYPTOCURRENCIES = [
    "BTC-USD",
    "ETH-USD",
    "DOGE-USD",  # Add Dogecoin
    # ... add more
]

# Adjust parameter ranges
STRATEGY_PARAMS = {
    "sma_crossover": {
        "short_window": [5, 10, 15, 20],  # More values to test
        "long_window": [50, 100, 150, 200],
    },
    # ... modify other strategies
}

# Change backtest settings
BACKTEST_CONFIG = {
    "initial_capital": 50000.0,  # Start with $50k
    "commission": 0.0015,  # 0.15% commission
    "data_period": "2y",  # 2 years of data
    "data_interval": "1h",  # Hourly data
}
```

## Adding New Strategies

1. Create a new strategy class in `robo/strategies.py`:

```python
class MyStrategy(Strategy):
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        # Your strategy logic here
        signals = pd.Series(0, index=data.index)
        # ... calculate signals
        return signals
    
    def get_param_names(self) -> List[str]:
        return ['param1', 'param2']
```

2. Register it in the STRATEGY_CLASSES dictionary:

```python
STRATEGY_CLASSES = {
    # ... existing strategies
    'my_strategy': MyStrategy,
}
```

3. Add parameters to `robo/config.py`:

```python
STRATEGY_PARAMS = {
    # ... existing params
    "my_strategy": {
        "param1": [10, 20, 30],
        "param2": [0.5, 1.0, 1.5],
    },
}
```

4. Run the sweep:

```bash
python sweep.py --strategies my_strategy
```

## Testing

Run the test suite:
```bash
python test_robo.py
```

## Tips

- Start with shorter periods (3mo, 6mo) to iterate quickly
- Use `--no-plots` flag to skip visualization if you only want CSV data
- Check `synthetic_results.csv` from the synthetic example to see the data format
- The bot handles missing data gracefully and continues with available data
- Use daily data (1d) for long-term strategies, hourly (1h) for short-term

## Performance Notes

- Each parameter combination is tested on each cryptocurrency
- Total tests = (param combinations) × (number of cryptos)
- Example: 10 SMA combinations × 5 cryptos = 50 tests
- Processing time depends on data size and number of tests
- Results are cached to speed up repeated runs

## Disclaimer

**This is for testing and experimentation purposes only.**
- Not financial advice
- Past performance does not guarantee future results
- Use at your own risk
- Always do your own research before trading
