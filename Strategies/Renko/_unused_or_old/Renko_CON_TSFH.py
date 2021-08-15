from Strategies.Renko.Renko_TSFH import Renko_TSFH
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMA import SMA 


# renko buy above high

class Renko_CON_TSFH(Renko_TSFH):
    NAME = RegisteredStrategyNames.RENKO_CON_TSFH

    def __init__(self, ticker, aggregation, smaLength, sellOutX):
        super().__init__(ticker, aggregation, sellOutX)
        self.lastGreenHigh = -1
        self.sma = SMA(smaLength)

        self.stock.setNewCandleListener(self.onNewCandle)

    def onNewCandle(self, newCandle):
        # is a red bar and last bar was green
        prevBar, newBar = self.stock.getLastTwoBars()
        if prevBar != None and newBar != None \
            and newBar.close < newBar.open and prevBar.close > prevBar.open:
            
            self.lastGreenHigh = prevBar.close

        # update studies:
        self.sma.add(newCandle.close)

        super().onNewCandle(newCandle)
        
        
    # is a green bar
    # is confirmation 
    # last was not a buy condition 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and self.sma.isDrawn() \
            and self.sma.isConfirmation(newCandle) \
            and not (previousCandle.close > previousCandle.open and self.sma.isConfirmation(previousCandle))
            

