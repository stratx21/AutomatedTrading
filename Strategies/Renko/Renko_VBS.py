from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

# Renko Variable Buy Sell 
class Renko_VBS(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_VBS

    def __init__(self, ticker, aggregation, buyAfterXGreen, sellAfterXRed):
        super().__init__(ticker, aggregation)
        self.buyAfterXGreen = buyAfterXGreen
        self.sellAfterXRed  = sellAfterXRed
        self.greenConsecutiveCount = 0
        self.redConsecutiveCount = 0

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):

        if newCandle.close > newCandle.open: # is a green bar 
            self.greenConsecutiveCount += 1
            self.redConsecutiveCount = 0
        else:
            self.redConsecutiveCount += 1
            self.greenConsecutiveCount = 0

        super().onNewCandle(newCandle)

    # enough red bars 
    def getSellCondition(self, newCandle, previousCandle):
        return self.redConsecutiveCount == self.sellAfterXRed
        
        
    # enough green bars 
    def getBuyCondition(self, newCandle, previousCandle):
        return self.greenConsecutiveCount == self.buyAfterXGreen

