from Chart.RenkoStock import RenkoStock
from Strategies.Renko.RenkoStrategy import RenkoStrategy
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames

# Renko with Context, Variable Sell 
class Renko_WC_VS(RenkoStrategy):
    NAME = RegisteredStrategyNames.RENKO_WCONTEXT_VS

    def __init__(self, ticker, aggregation, contextAggregation, sellAfterXRed):
        super().__init__(ticker, aggregation)
        self.sellAfterXRed  = sellAfterXRed
        self.redConsecutiveCount = 0

        self.stock.setNewCandleListener(self.onNewCandle)

        self.contextStock = RenkoStock(ticker, contextAggregation)
        self.contextStock.setNewCandleListener(self.onNewCandleContext)
        self.contextBarIsGreen = False 

    #Override
    def addPrice(self, price):
        super().addPrice(price)
        self.contextStock.addQuotePrice(price)

    #Override
    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        if newCandle.close > newCandle.open: # is a green bar 
            self.redConsecutiveCount = 0
        else:
            self.redConsecutiveCount += 1

        self.actionCheck()

    def onNewCandleContext(self, newCandle):
        self.contextBarIsGreen = newCandle.close >= newCandle.open
        self.actionCheck()

    # check if it should act (buy or sell)
    #  triggered by data changing, new candle for 
    #  either the chart or the context chart  
    def actionCheck(self):
        if self.inPosition:
            if self.getSellConditionCustom():
                self.sell()

        else:
            newBar = self.stock.getLastBar()
            if newBar != None and self.getBuyConditionCustom(newBar):
                self.buy()

    # enough red bars 
    def getSellConditionCustom(self):
        return self.redConsecutiveCount >= self.sellAfterXRed

    def getSellCondition(self, newCandle, previousCandle):
        return self.getSellCondition()
        
        
    # current and context are green
    def getBuyConditionCustom(self, newCandle):
        return newCandle.close > newCandle.open \
            and self.contextBarIsGreen

            
    def getBuyCondition(self, newCandle, previousCandle):
        return self.getBuyCondition(newCandle)

