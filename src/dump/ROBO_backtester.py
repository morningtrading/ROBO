"""
ROBO Backtester - Backtesting engine for trading strategies
"""

import pandas as pd
from backtesting import Backtest
from typing import Dict
from .utils.ROBO_logger import get_logger
from .strategies.ROBO_rsi_strategy import ROBORSIStrategy
from .strategies.ROBO_ema_strategy import ROBOEMAStrategy

logger = get_logger()


class ROBOBacktester:
    """Backtesting engine for ROBO strategies"""
    
    def __init__(self, config: dict):
        """
        Initialize backtester
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.strategy_name = config['strategy']['name']
        
        # Select strategy class
        if 'RSI' in self.strategy_name:
            self.strategy_class = ROBORSIStrategy
        elif 'EMA' in self.strategy_name:
            self.strategy_class = ROBOEMAStrategy
        else:
            self.strategy_class = ROBORSIStrategy
            logger.warning(f"Unknown strategy {self.strategy_name}, defaulting to RSI")
        
        # Set strategy parameters from config
        self._configure_strategy()
        
        logger.info(f"Initialized backtester with {self.strategy_name}")
    
    def _configure_strategy(self):
        """Configure strategy parameters from config"""
        indicators = self.config['indicators']
        risk = self.config['risk_management']
        
        # Configure trade direction
        self.strategy_class.TRADE_DIRECTION = self.config['trade_direction']
        
        # Configure ATR parameters
        self.strategy_class.ATR_PERIOD = indicators['atr']['period']
        self.strategy_class.ATR_SL_MULTIPLIER = risk['stop_loss']['atr_multiplier']
        self.strategy_class.ATR_TP_MULTIPLIER = risk['take_profit']['atr_multiplier']
        
        # Configure risk parameters
        self.strategy_class.RISK_PERCENT = risk['risk_per_trade_percent']
        self.strategy_class.MAX_POSITION_SIZE = risk['max_position_size_percent'] / 100
        
        # Configure strategy-specific parameters
        if hasattr(self.strategy_class, 'RSI_PERIOD'):
            # RSI strategy
            self.strategy_class.RSI_PERIOD = indicators['rsi']['period']
            self.strategy_class.RSI_OVERSOLD = indicators['rsi']['oversold']
            self.strategy_class.RSI_OVERBOUGHT = indicators['rsi']['overbought']
            self.strategy_class.SMA_PERIOD = indicators['sma_trend']['period']
            self.strategy_class.USE_SMA_FILTER = indicators['sma_trend']['enabled']
        
        if hasattr(self.strategy_class, 'EMA_FAST'):
            # EMA strategy
            self.strategy_class.EMA_FAST = indicators.get('ema', {}).get('fast', 9)
            self.strategy_class.EMA_SLOW = indicators.get('ema', {}).get('slow', 50)
            self.strategy_class.SMA_TREND = indicators['sma_trend']['period']
            self.strategy_class.USE_SMA_FILTER = indicators['sma_trend']['enabled']
    
    def run_backtest(self, symbol: str, data: pd.DataFrame) -> dict:
        """
        Run backtest on single symbol
        
        Args:
            symbol: Trading symbol
            data: OHLCV DataFrame
            
        Returns:
            dict: Backtest results
        """
        try:
            logger.info(f"{symbol}: Running backtest...")
            
            bt = Backtest(
                data,
                self.strategy_class,
                cash=self.config['backtest']['initial_capital'],
                commission=self.config['backtest']['commission'],
                exclusive_orders=True
            )
            
            stats = bt.run()
            
            result = {
                'symbol': symbol,
                'return_pct': stats['Return [%]'],
                'sharpe': stats['Sharpe Ratio'],
                'max_drawdown': stats['Max. Drawdown [%]'],
                'win_rate': stats['Win Rate [%]'],
                'num_trades': stats['# Trades'],
                'avg_trade': stats.get('Avg. Trade [%]', 0),
                'best_trade': stats.get('Best Trade [%]', 0),
                'worst_trade': stats.get('Worst Trade [%]', 0),
                'profit_factor': stats.get('Profit Factor', 0),
                'expectancy': stats.get('Expectancy [%]', 0),
            }
            
            logger.info(f"{symbol}: Backtest complete - Return: {result['return_pct']:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"{symbol}: Backtest failed: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'return_pct': 0,
                'sharpe': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'num_trades': 0
            }
    
    def run_all(self, market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Run backtests on all symbols
        
        Args:
            market_data: Dictionary of symbol -> DataFrame
            
        Returns:
            DataFrame with all results
        """
        results = []
        
        for symbol, data in market_data.items():
            result = self.run_backtest(symbol, data)
            results.append(result)
        
        return pd.DataFrame(results)
    
    def display_results(self, results: pd.DataFrame):
        """
        Display backtest results in formatted table
        
        Args:
            results: DataFrame with backtest results
        """
        print("\n" + "="*100)
        print(f"BACKTEST RESULTS - {self.strategy_name}".center(100))
        print("="*100)
        
        # Print header
        print(f"{'Symbol':<12} {'Return':>8} {'Sharpe':>7} {'Win%':>6} "
              f"{'Trades':>7} {'MaxDD':>8} {'PF':>6} {'Status':<10}")
        print("-"*100)
        
        # Print each result
        for _, row in results.iterrows():
            if 'error' in row and pd.notna(row['error']):
                status = "ERROR"
                color = "red"
            elif row['return_pct'] > 0:
                status = "PROFIT"
                color = "green"
            else:
                status = "LOSS"
                color = "red"
            
            print(f"{row['symbol']:<12} "
                  f"{row['return_pct']:>7.1f}% "
                  f"{row['sharpe']:>7.2f} "
                  f"{row['win_rate']:>6.1f}% "
                  f"{int(row['num_trades']):>7} "
                  f"{row['max_drawdown']:>7.1f}% "
                  f"{row.get('profit_factor', 0):>6.2f} "
                  f"{status:<10}")
        
        # Print summary
        print("-"*100)
        profitable = (results['return_pct'] > 0).sum()
        total = len(results)
        avg_return = results['return_pct'].mean()
        
        print(f"\nSUMMARY: {profitable}/{total} profitable | "
              f"Avg Return: {avg_return:.2f}%")
        print("="*100 + "\n")
    
    def save_results(self, results: pd.DataFrame, filepath: str):
        """
        Save results to CSV
        
        Args:
            results: DataFrame with results
            filepath: Output file path
        """
        try:
            results.to_csv(filepath, index=False)
            logger.info(f"Results saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
