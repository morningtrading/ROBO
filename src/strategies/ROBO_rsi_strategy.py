"""
ROBO RSI Strategy - RSI + SMA200 filter with ATR risk management
"""

import talib
from strategies.ROBO_base_strategy import ROBOBaseStrategy


class ROBORSIStrategy(ROBOBaseStrategy):
    """RSI-based mean reversion strategy with trend filter"""
    
    # Parameters (set from config)
    RSI_PERIOD = 14
    RSI_OVERSOLD = 35
    RSI_OVERBOUGHT = 65
    SMA_PERIOD = 200
    USE_SMA_FILTER = True
    TRADE_DIRECTION = "both"  # "long", "short", or "both"
    
    def init_indicators(self):
        """Initialize RSI and SMA indicators"""
        self.rsi = self.I(talib.RSI, self.data.Close, self.RSI_PERIOD)
        
        if self.USE_SMA_FILTER:
            self.sma200 = self.I(talib.SMA, self.data.Close, self.SMA_PERIOD)
    
    def check_entry_long(self) -> bool:
        """
        Long entry conditions:
        - RSI < oversold threshold
        - Price above SMA200 (if filter enabled)
        """
        if self.TRADE_DIRECTION not in ["long", "both"]:
            return False
        
        price = float(self.data.Close[-1])
        rsi = float(self.rsi[-1])
        
        # RSI oversold check
        if rsi >= self.RSI_OVERSOLD:
            return False
        
        # SMA trend filter
        if self.USE_SMA_FILTER:
            above_sma = price > float(self.sma200[-1])
            if not above_sma:
                return False
        
        return True
    
    def check_entry_short(self) -> bool:
        """
        Short entry conditions:
        - RSI > overbought threshold
        - Price below SMA200 (if filter enabled)
        """
        if self.TRADE_DIRECTION not in ["short", "both"]:
            return False
        
        price = float(self.data.Close[-1])
        rsi = float(self.rsi[-1])
        
        # RSI overbought check
        if rsi <= self.RSI_OVERBOUGHT:
            return False
        
        # SMA trend filter
        if self.USE_SMA_FILTER:
            below_sma = price < float(self.sma200[-1])
            if not below_sma:
                return False
        
        return True
    
    def check_exit_long(self) -> bool:
        """
        Exit long when RSI reaches overbought
        (Also exits via TP/SL from base class)
        """
        rsi = float(self.rsi[-1])
        return rsi >= self.RSI_OVERBOUGHT
    
    def check_exit_short(self) -> bool:
        """
        Exit short when RSI reaches oversold
        (Also exits via TP/SL from base class)
        """
        rsi = float(self.rsi[-1])
        return rsi <= self.RSI_OVERSOLD
