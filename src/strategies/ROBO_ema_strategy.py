"""
ROBO EMA Strategy - EMA crossover with SMA trend filter and ATR risk management
"""

import talib
from strategies.ROBO_base_strategy import ROBOBaseStrategy


class ROBOEMAStrategy(ROBOBaseStrategy):
    """EMA crossover strategy with long-term trend filter"""
    
    # Parameters (set from config)
    EMA_FAST = 9
    EMA_SLOW = 50
    SMA_TREND = 100
    USE_SMA_FILTER = True
    TRADE_DIRECTION = "long"  # "long", "short", or "both"
    
    def init_indicators(self):
        """Initialize EMA and SMA indicators"""
        self.ema_fast = self.I(talib.EMA, self.data.Close, self.EMA_FAST)
        self.ema_slow = self.I(talib.EMA, self.data.Close, self.EMA_SLOW)
        
        if self.USE_SMA_FILTER:
            self.sma_trend = self.I(talib.SMA, self.data.Close, self.SMA_TREND)
    
    def detect_bullish_cross(self) -> bool:
        """
        Detect EMA bullish crossover
        
        Returns:
            bool: True if fast EMA crossed above slow EMA
        """
        if len(self.ema_fast) < 2:
            return False
        
        current_fast = float(self.ema_fast[-1])
        current_slow = float(self.ema_slow[-1])
        prev_fast = float(self.ema_fast[-2])
        prev_slow = float(self.ema_slow[-2])
        
        return (current_fast > current_slow) and (prev_fast <= prev_slow)
    
    def detect_bearish_cross(self) -> bool:
        """
        Detect EMA bearish crossover
        
        Returns:
            bool: True if fast EMA crossed below slow EMA
        """
        if len(self.ema_fast) < 2:
            return False
        
        current_fast = float(self.ema_fast[-1])
        current_slow = float(self.ema_slow[-1])
        prev_fast = float(self.ema_fast[-2])
        prev_slow = float(self.ema_slow[-2])
        
        return (current_fast < current_slow) and (prev_fast >= prev_slow)
    
    def check_entry_long(self) -> bool:
        """
        Long entry conditions:
        - EMA fast crosses above EMA slow (bullish crossover)
        - Price above SMA trend filter (if enabled)
        """
        if self.TRADE_DIRECTION not in ["long", "both"]:
            return False
        
        # Check for bullish crossover
        if not self.detect_bullish_cross():
            return False
        
        # SMA trend filter
        if self.USE_SMA_FILTER:
            price = float(self.data.Close[-1])
            above_sma = price > float(self.sma_trend[-1])
            if not above_sma:
                return False
        
        return True
    
    def check_entry_short(self) -> bool:
        """
        Short entry conditions:
        - EMA fast crosses below EMA slow (bearish crossover)
        - Price below SMA trend filter (if enabled)
        """
        if self.TRADE_DIRECTION not in ["short", "both"]:
            return False
        
        # Check for bearish crossover
        if not self.detect_bearish_cross():
            return False
        
        # SMA trend filter
        if self.USE_SMA_FILTER:
            price = float(self.data.Close[-1])
            below_sma = price < float(self.sma_trend[-1])
            if not below_sma:
                return False
        
        return True
    
    def check_exit_long(self) -> bool:
        """
        Exit long when bearish crossover occurs
        (Also exits via TP/SL from base class)
        """
        return self.detect_bearish_cross()
    
    def check_exit_short(self) -> bool:
        """
        Exit short when bullish crossover occurs
        (Also exits via TP/SL from base class)
        """
        return self.detect_bullish_cross()
