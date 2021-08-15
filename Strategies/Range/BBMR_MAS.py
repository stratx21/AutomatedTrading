import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Strategies.Range.BBMR import BBMR
from Studies.SMA import SMA 

class BBMR_MAS(BBMR):
    NAME = RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE_MAS
    
    def __init__(self, ticker, aggregation, smaLength):
        super().__init__(ticker, aggregation, smaLength, None)

        self.smaLength = int(smaLength) 
        
        # override candle listener 
        self.stock.setNewCandleListener(self.onNewCandle)
        
        self.sma = SMA(int(smaLength))
        
    # keep super.addPrice
    
    def onNewCandle(self, newCandle):
        self.sma.add(newCandle.close)
        super().onNewCandle(newCandle)
        
    
    # BBMR condition
    # midline > sma  
    def getBuyCondition(self, newCandle, previousCandle):
        #print("midline:", self.bollingerBands.midLine.getLatestValue(), " sma:", self.sma.getLatestValue(), " lower band:", self.bollingerBands.lowerBand.getLatestValue(), " upper band:", self.bollingerBands.upperBand.getLatestValue())
        return super().getBuyCondition(newCandle, previousCandle) \
            and self.sma.isDrawn() \
            and self.bollingerBands.aboveMidline(self.sma.getLatestValue()) 
            


