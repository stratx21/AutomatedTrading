from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

# renko sell after _x_ candles 

class Renko_SA(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_SA

    def __init__(self, ticker, aggregation, sellAtXGreenBricks):
        super().__init__(ticker, aggregation)
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
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open \
            or self.greenConsecutiveCount >= self.sellAtXGreenBricks
        
        
    # enough green bars 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and previousCandle.open > previousCandle.close