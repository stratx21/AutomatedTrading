from Strategies.Renko.Renko_BAH import Renko_BAH
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

class Renko_BAH_SA(Renko_BAH):
    NAME = RegisteredStrategyNames.RENKO_BAH_SA

    def __init__(self, ticker, aggregation, sellAtXGreenBricks):
        super().__init__(ticker, aggregation)
        self.sellAtXGreenBricks = sellAtXGreenBricks
        self.greenConsecutiveCount = 0

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        if newCandle.close > newCandle.open: # is a green bar 
            self.greenConsecutiveCount += 1
        else:
            self.greenConsecutiveCount = 0

        prevBar, newBar = self.stock.getLastTwoBars()

        if prevBar != None and newBar != None:
            if self.inPosition:
                if self.getSellCondition(newBar, prevBar):
                    self.sell()

            else:
                if self.getBuyCondition(newBar, prevBar):
                    self.buy()


    # is a red bar
    # OR
    # at x green bars to sell 
    #@Override
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open \
            or self.greenConsecutiveCount >= self.sellAtXGreenBricks

    def getBuyCondition(self, newCandle, previousCandle):
        return super().getBuyCondition(newCandle, previousCandle)
        