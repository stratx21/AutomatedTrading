from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMA import SMA 


# renko Confirmation and Validation

class Renko_CaV(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_CaV

    def __init__(self, ticker, aggregation, smaLength):
        super().__init__(ticker, aggregation)

        self.sma = SMA(smaLength)

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        # update studies:
        self.sma.add(newCandle.close)

        super().onNewCandle(newCandle)


    # is a red bar
    def getSellCondition(self, newCandle, previousCandle):
        return self.sma.isConservativeValidation(newCandle)
        
        
    # is a green bar
    # is confirmation 
    # last was not a buy condition 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and self.sma.isDrawn() \
            and self.sma.isConfirmation(newCandle) \
            and not (previousCandle.close > previousCandle.open and self.sma.isConfirmation(previousCandle))
            


