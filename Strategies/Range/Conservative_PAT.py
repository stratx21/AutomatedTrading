from Strategies.Range.RangeStrategy import RangeStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

class Conservative_PAT(RangeStrategy):
    NAME = RegisteredStrategyNames.CONSERVATIVE_PAT

    def __init__(self, ticker, aggregation, marginOfSell = 0.00):
        super().__init__(ticker, aggregation)
        self.stock.setNewCandleListener(self.onNewCandle)
        self.marginOfSell = marginOfSell  #[NOTE IN DOLLARS] can go $[marginOfSell] below prev bar low before selling

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

        # in position - calculate if should sell 
        if self.inPosition:
            if self.getSellCondition(self.stock.getLastBar(), price): 
                self.sell()

    #Override
    def onNewCandle(self, newCandle):
        #update studies...
        # (none)

        self.outputCandleData(newCandle)

        secondtolastbar, lastbar = self.stock.getLastTwoBars()

        if secondtolastbar != None and lastbar != None:
            # not in position - calculate if should buy
            if not self.inPosition:
                if self.getBuyCondition(secondtolastbar, lastbar):
                    self.buy()

        # TODO could add else and call super()'s get sell condition to sell if 
        #   bar closed and is below (original sell) - if using the marginOfSell
    
    # separate so it can be used in other strategies too: 

    def getSellCondition(self, lastbar, newprice):
        # red bar and close < last bar low 
        return newprice < lastbar.getLowIgnoringWicks() - self.marginOfSell
            
    def getBuyCondition(self, secondtolastbar, lastbar):
        # green bar and close > last bar high 
        return lastbar.close >= lastbar.open and lastbar.close > secondtolastbar.getHighIgnoringWicks()
