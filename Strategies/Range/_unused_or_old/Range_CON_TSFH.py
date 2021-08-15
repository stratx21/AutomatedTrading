from Strategies.Range.Range_CaV import Range_CaV 
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMA import SMA

# Range SMI TSFH
class Range_CON_TSFH(Range_CaV):
    NAME = RegisteredStrategyNames.RANGE_CON_TSFH 

    def __init__(self, ticker, aggregation, smaLength, sellOutX):
        super().__init__(ticker, aggregation, smaLength)
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

    #@Override
    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        # update studies: 
        self.sma.add(newCandle.close)

        prevBar, newBar = self.stock.getLastTwoBars()

        if prevBar != None and newBar != None and not self.inPosition:
            if self.getBuyCondition(newBar, prevBar):
                self.buy()
                self.high = newBar.close 


    def getTickDeterminedSellCondition(self, price):
        if price > self.high:
            self.high = price 
        return price < self.high - self.sellOutX

