from Strategies.Range.PriceActionTrader import PriceActionTrader
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMA import SMA

class PAT_SMAgreen_LastbarnotPAT(PriceActionTrader):
    NAME = RegisteredStrategyNames.PAT_SMAisG_LastNPAT

    def __init__(self, ticker, aggregation, smaLength):
        super().__init__(ticker, aggregation)
        self.stock.setNewCandleListener(self.onNewCandle)
        # ^ runs after super so this will be the listener 

        self.sma = SMA(int(smaLength))

    # use super's addPrice 

    def onNewCandle(self, newCandle):
        #update studies...
        self.sma.add(newCandle.close)
        
        # if not self.sma.isGreen():
        #     print("REDDDD")
        # print("EMA val: ", self.sma.getLatestValue())

        super().onNewCandle(newCandle)


    # only the buy condition is changed/added to: 

    def getBuyCondition(self, secondtolastbar, lastbar):
        # PAT buy, SMA positive velocity, and last bar was not PAT buy 
        return super().getBuyCondition(secondtolastbar, lastbar) \
            and self.sma.isDrawn() \
            and self.sma.isGreen() \
            and not super().getBuyCondition(self.stock.getXBarsAgo(3), secondtolastbar)

