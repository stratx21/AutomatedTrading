import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.BollingerBands import BollingerBands
from Strategies.Range.RangeStrategy import RangeStrategy 

class BBMR(RangeStrategy):
    NAME = RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE
    
    def __init__(self, ticker, aggregation, arg1 = None, arg2 = None):
        super().__init__(ticker, aggregation)
        
        # override super listener (NOTE : no super listener)
        self.stock.setNewCandleListener(self.onNewCandle)
        
        self.bollingerBands = BollingerBands(20, -1.5, 1.5)
        
        
    #@Override
    def addPrice(self, price):
        super().addPrice(price)
        
    #@Override
    def onNewCandle(self, newCandle):
        self.bollingerBands.add(newCandle.close)
        
        super().onNewCandle(newCandle)
                
                
    # [stoploss] low < lowerBand
    # OR (
    # [target] high higher than upper band on this bar or previous bar 
    #                                             (high > upperBand OR prevBar.high > upperBand[1])
    # [target] close is lower than upper band     (close < upperBand)
    # 
    def getSellCondition(self, newCandle, previousCandle):
        return self.bollingerBands.belowLowerBand(newCandle.low) \
            or ( \
                ( \
                    self.bollingerBands.aboveUpperBand(newCandle.high) \
                    or \
                    self.bollingerBands.aboveUpperBandOneBarAgo(previousCandle.high) \
                ) \
                and self.bollingerBands.belowUpperBand(newCandle.close) \
            )
        
        
    # close > open    # NOTE: not a concern for range bars for this 
    # close > midline 
    # low < midline
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.close > newCandle.open \
            and self.bollingerBands.isDrawn() \
            and self.bollingerBands.aboveMidline(newCandle.close) \
            and self.bollingerBands.belowMidline(newCandle.low) 
            
        