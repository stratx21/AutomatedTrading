from Strategies.Range.Range_SMI import Range_SMI 
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

# Range SMI TSFH
class Range_SMI_TSFH(Range_SMI):
    NAME = RegisteredStrategyNames.RANGE_SMI_TSFH 

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

    #@Override
    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        prevBar, newBar = self.stock.getLastTwoBars()

        self.smi.add(newCandle)

        if prevBar != None and newBar != None and not self.inPosition:
            if self.getBuyCondition(newBar, prevBar):
                self.buy()
                self.high = newBar.close 


    def getTickDeterminedSellCondition(self, price):
        if price > self.high:
            self.high = price 
        return price < self.high - self.sellOutX

