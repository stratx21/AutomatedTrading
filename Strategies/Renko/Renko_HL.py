from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames


# renko buy higher low

class Renko_HL(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_HL

    def __init__(self, ticker, aggregation, includeDoubleBottoms = 0):
        super().__init__(ticker, aggregation)

        self.prevRedCount = -1 
        self.recentRedCount = -1
        self.redCount = 0 

        self.includeDoubleBottoms = includeDoubleBottoms > 0

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        # red 
        if newCandle.close < newCandle.open:
            self.redCount += 1
        else: # green 
            self.recentRedCount = self.redCount
            self.prevRedCount = self.recentRedCount
            self.redCount = 0

        super().onNewCandle(newCandle)



    # is a red bar
    def getSellCondition(self, newCandle, previousCandle):
        return newCandle.close < newCandle.open 
        
        
    # is a green bar
    # last bar was red 
    # higher low 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.open < newCandle.close \
            and previousCandle.open > previousCandle.close \
            and ( \
                (self.recentRedCount < self.prevRedCount and not self.includeDoubleBottoms) \
                or \
                (self.recentRedCount <= self.prevRedCount and self.includeDoubleBottoms) \
            )
            


