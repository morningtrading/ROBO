"""
Backtesting engine for evaluating trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .strategies import Strategy


class BacktestResult:
    """Container for backtest results."""
    
    def __init__(self, strategy_name: str, params: Dict[str, Any], symbol: str):
        self.strategy_name = strategy_name
        self.params = params
        self.symbol = symbol
        self.total_return = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.final_capital = 0.0
        self.trades = []
    
    def __str__(self):
        return (f"{self.strategy_name} on {self.symbol}: "
                f"Return={self.total_return:.2f}%, "
                f"Trades={self.total_trades}, "
                f"Sharpe={self.sharpe_ratio:.2f}")
    
    def to_dict(self):
        """Convert result to dictionary."""
        return {
            'strategy': self.strategy_name,
            'symbol': self.symbol,
            'params': str(self.params),
            'total_return': self.total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'final_capital': self.final_capital,
        }


class Backtester:
    """Backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate per trade (e.g., 0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
    
    def backtest(self, strategy: Strategy, data: pd.DataFrame, symbol: str) -> BacktestResult:
        """
        Run backtest on a strategy with given data.
        
        Args:
            strategy: Trading strategy instance
            data: Historical price data
            symbol: Cryptocurrency symbol
            
        Returns:
            BacktestResult with performance metrics
        """
        result = BacktestResult(strategy.__class__.__name__, strategy.params, symbol)
        
        # Make a copy to avoid modifying original data
        data = data.copy()
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        # Initialize portfolio
        capital = self.initial_capital
        position = 0  # 0 = no position, 1 = long position
        entry_price = 0
        trades = []
        equity_curve = []
        
        for i in range(len(data)):
            current_price = data['Close'].iloc[i]
            signal = signals.iloc[i]
            
            # Track equity
            equity = capital
            if position > 0:
                equity = capital + (position * current_price)
            equity_curve.append(equity)
            
            # Execute trades based on signals
            if signal == 1 and position == 0:  # Buy signal
                # Enter long position
                position = capital / current_price
                position *= (1 - self.commission)  # Deduct commission
                entry_price = current_price
                capital = 0
                trades.append({
                    'type': 'BUY',
                    'price': current_price,
                    'date': data.index[i],
                })
                
            elif signal == -1 and position > 0:  # Sell signal
                # Exit long position
                capital = position * current_price
                capital *= (1 - self.commission)  # Deduct commission
                
                # Calculate trade return
                trade_return = (current_price - entry_price) / entry_price * 100
                if trade_return > 0:
                    result.winning_trades += 1
                else:
                    result.losing_trades += 1
                
                trades.append({
                    'type': 'SELL',
                    'price': current_price,
                    'date': data.index[i],
                    'return': trade_return,
                })
                
                position = 0
                result.total_trades += 1
        
        # Close any open position at the end
        if position > 0:
            final_price = data['Close'].iloc[-1]
            capital = position * current_price
            capital *= (1 - self.commission)
            
            trade_return = (final_price - entry_price) / entry_price * 100
            if trade_return > 0:
                result.winning_trades += 1
            else:
                result.losing_trades += 1
            
            result.total_trades += 1
        
        # Calculate metrics
        result.final_capital = capital
        result.total_return = (capital - self.initial_capital) / self.initial_capital * 100
        result.trades = trades
        
        # Calculate max drawdown
        if equity_curve:
            equity_series = pd.Series(equity_curve)
            rolling_max = equity_series.expanding().max()
            drawdown = (equity_series - rolling_max) / rolling_max * 100
            result.max_drawdown = drawdown.min()
        
        # Calculate Sharpe ratio (simplified)
        if len(equity_curve) > 1:
            returns = pd.Series(equity_curve).pct_change().dropna()
            if returns.std() != 0:
                result.sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Annualized
        
        return result
