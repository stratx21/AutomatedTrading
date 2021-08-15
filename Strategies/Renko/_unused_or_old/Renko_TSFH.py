from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames


# Renko Trailing Stoploss, Following High
# 
# essentially a trailing stoploss, selling point 
#  increases as the highest price it has reached
#  increases.
class Renko_TSFH(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_TSFH

    # sellOutX: amount below highest high to sell at
    # example: to create a stoploss of 40 cents below the highest 
    # high, set to 0.40 
    def __init__(self, ticker, aggregation, sellOutX):
        super().__init__(ticker, aggregation)
        self.sellOutX = sellOutX / 100.0 # convert to cents from $ 
        self.high = -1.00

        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

        # sell stoploss based on tick, every new price
        if self.inPosition:
            if self.getTickDeterminedSellCondition(price):
                self.sell()


    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        prevBar, newBar = self.stock.getLastTwoBars()

        if prevBar != None and newBar != None and not self.inPosition \
            and self.getBuyCondition(newBar, prevBar):
            
            # buy, and set high now that a position is taken
            self.buy()
            self.high = newBar.close 

    def getTickDeterminedSellCondition(self, price):
        if price > self.high:
            self.high = price 
        return price < self.high - self.sellOutX
        
        
    # enough green bars 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.close > newCandle.open 

