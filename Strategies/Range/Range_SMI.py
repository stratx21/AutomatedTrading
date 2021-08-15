from Strategies.Range.RangeStrategy import RangeStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMI import SMI

# Range SMI
class Range_SMI(RangeStrategy):
    NAME = RegisteredStrategyNames.RANGE_SMI

    def __init__(self, ticker, aggregation, percentDLength=3, percentKLength=5):
        super().__init__(ticker, aggregation)

        self.smi = SMI(percentDLength=percentDLength, percentKLength=percentKLength)  

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        self.smi.add(newCandle)

        super().onNewCandle(newCandle)

    # enough red bars 
    def getSellCondition(self, newCandle, previousCandle):
        return not self.smi.isCrossed()
        
        
    # enough green bars 
    def getBuyCondition(self, newCandle, previousCandle):
        return self.smi.isCrossed()

