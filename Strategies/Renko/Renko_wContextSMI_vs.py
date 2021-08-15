from Strategies.Renko.Renko_wContext_VS import Renko_WC_VS
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.SMI import SMI

class Renko_WCSMI_VS(Renko_WC_VS):
    NAME = RegisteredStrategyNames.RENKO_WCONTEXTSMI_VS

    def __init__(self, ticker, aggregation, contextAggregation, sellAfterXRed):
        super().__init__(ticker, aggregation, contextAggregation, sellAfterXRed)

        self.contextSMI = SMI() # default 

        
    def onNewCandleContext(self, newCandle):
        self.contextSMI.add(newCandle)
        super().onNewCandleContext(newCandle)

    # current bar is green
    # and context SMI is crossed 
    def getBuyCondition(self, newCandle, previousCandle):
        return newCandle.close > newCandle.open \
            and self.contextSMI.isCrossed()
