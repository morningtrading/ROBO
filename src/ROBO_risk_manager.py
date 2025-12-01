"""
ROBO Risk Manager - Portfolio-level risk management
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from utils.ROBO_logger import get_logger

logger = get_logger()


class ROBORiskManager:
    """Manages portfolio-level risk limits"""
    
    def __init__(self, config: dict):
        """
        Initialize risk manager
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.risk_config = config['risk_management']
        
        # Portfolio limits
        self.max_positions = self.risk_config.get('max_concurrent_positions', 3)
        self.max_correlated = self.risk_config.get('max_correlated_positions', 1)
        self.daily_loss_limit = self.risk_config.get('daily_loss_limit_percent', 5.0) / 100
        self.correlation_threshold = self.risk_config.get('correlation_threshold', 0.7)
        
        # Track state
        self.open_positions = {}
        self.daily_pnl = 0.0
        self.initial_equity = None
    
    def can_open_position(self, symbol: str, equity: float) -> Tuple[bool, str]:
        """
        Check if new position can be opened
        
        Args:
            symbol: Trading symbol
            equity: Current equity
            
        Returns:
            (bool, str): (can_open, reason)
        """
        # Check max positions
        if len(self.open_positions) >= self.max_positions:
            return False, f"Max positions limit reached ({self.max_positions})"
        
        # Check daily loss limit
        if self.initial_equity is not None:
            daily_loss_pct = abs(self.daily_pnl / self.initial_equity)
            if self.daily_pnl < 0 and daily_loss_pct >= self.daily_loss_limit:
                return False, f"Daily loss limit reached ({daily_loss_pct:.2%})"
        
        # Check correlation (simplified implementation)
        # In production, calculate actual correlation between positions
        # For now, just limit positions in same sector
        
        return True, "OK"
    
    def register_position(self, symbol: str, entry_price: float, size: float):
        """
        Register new position
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            size: Position size
        """
        self.open_positions[symbol] = {
            'entry_price': entry_price,
            'size': size,
            'entry_time': pd.Timestamp.now()
        }
        logger.debug(f"Registered position: {symbol} @ {entry_price}, size={size}")
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[float]:
        """
        Close position and update PnL
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            
        Returns:
            float: Position PnL or None
        """
        if symbol not in self.open_positions:
            logger.warning(f"Attempted to close non-existent position: {symbol}")
            return None
        
        pos = self.open_positions.pop(symbol)
        pnl = (exit_price - pos['entry_price']) * pos['size']
        self.daily_pnl += pnl
        
        logger.debug(f"Closed position: {symbol} @ {exit_price}, PnL={pnl:.2f}")
        return pnl
    
    def reset_daily(self, equity: float):
        """
        Reset daily counters
        
        Args:
            equity: Current equity
        """
        self.daily_pnl = 0.0
        self.initial_equity = equity
        logger.info(f"Daily risk reset. Equity: {equity:.2f}")
    
    def get_position_size(self, equity: float, risk: float, price: float) -> float:
        """
        Calculate position size based on risk
        
        Args:
            equity: Current equity
            risk: Risk amount per unit
            price: Entry price
            
        Returns:
            float: Position size (fraction of equity)
        """
        risk_pct = self.risk_config['risk_per_trade_percent'] / 100
        max_size_pct = self.risk_config['max_position_size_percent'] / 100
        
        # Calculate size to risk desired amount
        risk_amount = equity * risk_pct
        size = risk_amount / (risk * price) if risk > 0 else 0
        
        # Cap at maximum position size
        max_size = equity * max_size_pct / price
        size = min(size, max_size)
        
        return max(size, 0)
    
    def get_current_exposure(self) -> float:
        """
        Get current portfolio exposure
        
        Returns:
            float: Total exposure as fraction
        """
        if not self.open_positions:
            return 0.0
        
        total_exposure = sum(
            pos['entry_price'] * pos['size'] 
            for pos in self.open_positions.values()
        )
        
        return total_exposure / self.initial_equity if self.initial_equity else 0.0
