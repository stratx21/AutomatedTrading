from Strategies.Renko.Renko_TSFH import Renko_TSFH
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames


# renko buy above high

class Renko_BAH_TSFH(Renko_TSFH):
    NAME = RegisteredStrategyNames.RENKO_BAH_TSFH

    def __init__(self, ticker, aggregation, sellOutX):
        super().__init__(ticker, aggregation, sellOutX)
        self.lastGreenHigh = -1

        self.stock.setNewCandleListener(self.onNewCandle)

    def onNewCandle(self, newCandle):
        # is a red bar and last bar was green
        prevBar, newBar = self.stock.getLastTwoBars()
        if prevBar != None and newBar != None \
            and newBar.close < newBar.open and prevBar.close > prevBar.open:

            self.lastGreenHigh = prevBar.close

        super().onNewCandle(newCandle)
        
        
    # is a green bar
    # close > lastGreenHigh
    # previous candle was under the last green high 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and newCandle.close > self.lastGreenHigh \
            and previousCandle.open < self.lastGreenHigh
            


