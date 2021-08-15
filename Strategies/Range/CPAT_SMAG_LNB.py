from Strategies.Range.Conservative_PAT import Conservative_PAT
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMA import SMA 

# Conservative PAT, SMA is green, last bar not a PAT buy
# 

class CPAT_SMAG_LNB(Conservative_PAT):
    NAME = RegisteredStrategyNames.CPAT_SMAG_LastNPAT

    def __init__(self, ticker, aggregation, smaLength, marginOfSell = 0.00):
        super().__init__(ticker,aggregation,marginOfSell)
        self.smaLength = int(smaLength)
        #override super's listener:
        self.stock.setNewCandleListener(self.onNewCandle)

        self.sma = SMA(int(smaLength))

    # keep super.addPrice

    def onNewCandle(self, newCandle):
        # update studies... 
        self.sma.add(newCandle.close)

        super().onNewCandle(newCandle)


    def getBuyCondition(self, secondtolastbar, lastbar):
        # CPAT buy, SMA velocity is positive, and last bar was NOT a CPAT buy
        return super().getBuyCondition(secondtolastbar, lastbar) \
            and self.sma.isDrawn() \
            and self.sma.isGreen() \
            and not super().getBuyCondition(self.stock.getXBarsAgo(3), secondtolastbar)
