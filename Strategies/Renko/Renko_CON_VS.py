from Strategies.Renko.Renko_CaV import Renko_CaV
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

class Renko_CON_VS(Renko_CaV):
    NAME = RegisteredStrategyNames.RENKO_CON_VS

    def __init__(self, ticker, aggregation, smaLength, sellAtXRedBricks):
        super().__init__(ticker, aggregation, smaLength)
        self.sellAtXRedBricks = sellAtXRedBricks
        self.redConsecutiveCount = 0

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        if newCandle.close < newCandle.open: # is a red bar 
            self.redConsecutiveCount += 1
        else:
            self.redConsecutiveCount = 0

        super().onNewCandle(newCandle)


    # is a red bar
    # AND
    # at x red bars to sell 
    #@Override
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open \
            and self.redConsecutiveCount >= self.sellAtXRedBricks
        
