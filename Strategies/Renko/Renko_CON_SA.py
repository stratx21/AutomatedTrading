from Strategies.Renko.Renko_CaV import Renko_CaV
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

class Renko_CON_SA(Renko_CaV):
    NAME = RegisteredStrategyNames.RENKO_CON_SA

    def __init__(self, ticker, aggregation, smaLength, sellAtXGreenBricks):
        super().__init__(ticker, aggregation, smaLength)
        self.sellAtXGreenBricks = sellAtXGreenBricks
        self.greenConsecutiveCount = 0

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        if newCandle.close > newCandle.open: # is a green bar 
            self.greenConsecutiveCount += 1
        else:
            self.greenConsecutiveCount = 0

        super().onNewCandle(newCandle)


    # is a red bar
    # OR
    # at x green bars to sell 
    #@Override
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open \
            or self.greenConsecutiveCount >= self.sellAtXGreenBricks
        
