from Strategies.Range.RangeStrategy import RangeStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

class PriceActionTrader(RangeStrategy):
    NAME = RegisteredStrategyNames.PRICE_ACTION_TRADER

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)
        self.stock.setNewCandleListener(self.onNewCandle)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    def onNewCandle(self, newCandle):
        
        super().onNewCandle(newCandle)
    
    # separate so it can be used in other strategies too: 

    def getSellCondition(self, secondtolastbar, lastbar):
        # red bar and close < last bar low 
        print("EEEEEEEEEEEEEEEEEEEEEE")
        return lastbar.close <= lastbar.open and lastbar.close < secondtolastbar.getLowIgnoringWicks()
            
    def getBuyCondition(self, secondtolastbar, lastbar):
        # green bar and close > last bar high 
        return lastbar.close >= lastbar.open and lastbar.close > secondtolastbar.getHighIgnoringWicks()
