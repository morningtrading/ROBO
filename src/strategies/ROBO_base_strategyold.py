"""
ROBO Base Strategy - Abstract base class for all strategies
"""

from abc import ABC, abstractmethod
import talib
import pandas as pd
from backtesting import Strategy
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ROBO_logger import get_logger

logger = get_logger()


class ROBOBaseStrategy(Strategy, ABC):
    """Base class for ROBO trading strategies"""
    
    # Configuration (will be set by child classes or externally)
    config = None
    
    # Default ATR settings
    ATR_PERIOD = 14
    ATR_SL_MULTIPLIER = 1.5
    ATR_TP_MULTIPLIER = 3.0
    
    # Default risk settings
    RISK_PERCENT = 2.0
    MAX_POSITION_SIZE = 0.95
    
    def init(self):
        """Initialize indicators - called once at start"""
        # Calculate ATR for all strategies
        self.atr = self.I(
            talib.ATR, 
            self.data.High, 
            self.data.Low, 
            self.data.Close, 
            self.ATR_PERIOD
        )
        
        # Call child class initialization
        self.init_indicators()
        
        logger.debug(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def init_indicators(self):
        """Initialize strategy-specific indicators - implemented by child classes"""
        pass
    
    @abstractmethod
    def check_entry_long(self) -> bool:
        """Check if long entry conditions are met"""
        pass
    
    @abstractmethod
    def check_entry_short(self) -> bool:
        """Check if short entry conditions are met"""
        pass
    
    @abstractmethod
    def check_exit_long(self) -> bool:
        """Check if long exit conditions are met"""
        pass
    
    @abstractmethod
    def check_exit_short(self) -> bool:
        """Check if short exit conditions are met"""
        pass
    
    def calculate_position_size(self, risk_per_unit: float) -> float:
        """
        Calculate position size based on risk
        
        Args:
            risk_per_unit: Risk amount per price unit
            
        Returns:
            float: Position size as fraction
        """
        if risk_per_unit <= 0:
            return 0
        
        risk_amount = self.equity * (self.RISK_PERCENT / 100)
        price = float(self.data.Close[-1])
        size = risk_amount / (risk_per_unit * price)
        
        # Cap at maximum
        size = min(size, self.MAX_POSITION_SIZE)
        
        return size if size > 0.001 else 0
    
    def get_atr_stop_loss(self, is_long: bool) -> float:
        """
        Calculate ATR-based stop loss
        
        Args:
            is_long: True for long position, False for short
            
        Returns:
            float: Stop loss price
        """
        price = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        
        if is_long:
            return price - (self.ATR_SL_MULTIPLIER * atr)
        else:
            return price + (self.ATR_SL_MULTIPLIER * atr)
    
    def get_atr_take_profit(self, is_long: bool) -> float:
        """
        Calculate ATR-based take profit
        
        Args:
            is_long: True for long position, False for short
            
        Returns:
            float: Take profit price
        """
        price = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        
        if is_long:
            return price + (self.ATR_TP_MULTIPLIER * atr)
        else:
            return price - (self.ATR_TP_MULTIPLIER * atr)
    
    def next(self):
        """Main strategy logic - called for each bar"""
        # Skip if not enough data
        if len(self.data) < max(self.ATR_PERIOD, 200):
            return
        
        price = float(self.data.Close[-1])
        
        # Handle existing position
        if self.position:
            if self.position.is_long and self.check_exit_long():
                self.position.close()
                return
            elif self.position.is_short and self.check_exit_short():
                self.position.close()
                return
        
        # Check for new entries
        if not self.position:
            # Long entry
            if self.check_entry_long():
                sl = self.get_atr_stop_loss(is_long=True)
                tp = self.get_atr_take_profit(is_long=True)
                risk = price - sl
                size = self.calculate_position_size(risk)
                
                if size > 0:
                    self.buy(sl=sl, tp=tp, size=size)
            
            # Short entry
            elif self.check_entry_short():
                sl = self.get_atr_stop_loss(is_long=False)
                tp = self.get_atr_take_profit(is_long=False)
                risk = sl - price
                size = self.calculate_position_size(risk)
                
                if size > 0:
                    self.sell(sl=sl, tp=tp, size=size)
