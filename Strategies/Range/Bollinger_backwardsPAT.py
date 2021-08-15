from Strategies.Range.PriceActionTrader import PriceActionTrader
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames 
from Studies.BollingerBands import BollingerBands

# AKA dumb_WORKING

class BB_bPAT(PriceActionTrader):
    NAME = RegisteredStrategyNames.BOLLINGER_BACKWARDS_PAT

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)

        #override super listeners: 
        self.stock.setNewCandleListener(self.onNewCandle)
        
        self.bollingerBands = BollingerBands(10, -1.5, 2.0)

    #@Override
    def addPrice(self, price):
        super().addPrice(price)
        
    #@Override
    def onNewCandle(self, newCandle):

        self.bollingerBands.add(newCandle.close)

        super().onNewCandle(newCandle)


    # sell condition: 
    # (green)                     is green bar 
    # (close > max(close|open)    close > high (ignoring wicks, highest of open or close) of prev bar
    # (PAT_LNB)                   previous candle was NOT a PAT buy 
    # (BB.UB increasing)          BollingerBands UpperBand is increasing
    def getSellCondition(self, secondtolastbar, lastbar):
        return lastbar.close > lastbar.open \
            and lastbar.close > secondtolastbar.getHighIgnoringWicks() \
            and not super().getBuyCondition(self.stock.getXBarsAgo(3), secondtolastbar) \
            and self.bollingerBands.upperBandIsIncreasing()


    def getBuyCondition(self, secondtolastbar, lastbar):
        return lastbar.close > lastbar.open \
            and ( \
                self.bollingerBands.belowLowerBand(lastbar.low) \
                or \
                self.bollingerBands.belowLowerBandOneBarAgo(secondtolastbar.low) \
            ) \
            and self.bollingerBands.isDrawn()
                


