from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames


# renko buy above high

class Renko_BAH(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_BAH

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)
        self.lastGreenHigh = -1

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        prevBar, newBar = self.stock.getLastTwoBars()

        if prevBar != None and newBar != None:
            # is a red bar and last bar was green:
            if newBar.close < newBar.open and prevBar.close > prevBar.open:
                self.lastGreenHigh = prevBar.close

            if self.inPosition:
                if self.getSellCondition(newBar, prevBar):
                    self.sell()

            else:
                if self.getBuyCondition(newBar, prevBar):
                    self.buy()



    # is a red bar
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open 
        
        
    # is a green bar
    # close > lastGreenHigh
    # previous candle was under the last green high 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and newCandle.close > self.lastGreenHigh \
            and previousCandle.open < self.lastGreenHigh
            


