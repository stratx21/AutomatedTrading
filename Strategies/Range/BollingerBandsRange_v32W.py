import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Studies.BollingerBands import BollingerBands
from Strategies.Range.RangeStrategy import RangeStrategy

class BBR_v32W(RangeStrategy):
    NAME = RegisteredStrategyNames.BOLLINGER_RANGE_V32W

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)

        #override super listener: # note - no super listener in Strategy
        self.stock.setNewCandleListener(self.onNewCandle)

        # thinkscript has 2, but 3 instead for width check, because
        #  it is checking with [] in thinkscript, meaning it is
        #  comparing: 
        #    bandwidth > bandwidth[2]
        #, AKA, bandwidth now > bandwith 2 bars ago
        # 
        #  thus the queue needs to have 3, to have the current
        #  bar and 2 bars ago 
        self.bollingerBands = BollingerBands(20, -1.5, 1.5, 3)


    #@Override
    def addPrice(self, price):
        super().addPrice(price)

    #@Override
    def onNewCandle(self, newCandle):
        self.bollingerBands.add(newCandle.close)

        super().onNewCandle(newCandle)


    # red bar (close < open)
    # prev bar green (prev bar close > prev bar open) 
    # prev close > max(open,close) of 2 bars ago
    # (prev high > upper band from 1 bar ago 
    #   OR high > upper band)
    def getSellCondition(self, newCandle, previousCandle):
        thirdBarBack = self.stock.getXBarsAgo(3)
        return newCandle.close < newCandle.open \
            and previousCandle.close > previousCandle.open \
            and previousCandle.close > thirdBarBack.getHighIgnoringWicks() \
            and ( \
                self.bollingerBands.aboveUpperBandOneBarAgo(previousCandle.high) \
                or \
                self.bollingerBands.aboveUpperBand(newCandle.high) \
            )


    # green bar (close > open)
    # low of previous bar < lower band from previous bar
    # bandwidth has increased
    def getBuyCondition(self, newCandle, previousCandle):
        # print("buy condition: first: ", newCandle.close > newCandle.open,\
        #     "second: ", self.bollingerBands.belowLowerBandOneBarAgo(previousCandle.low), \
        #     "third: ", self.bollingerBands.bandwidthHasIncreased())
        return newCandle.close > newCandle.open \
            and self.bollingerBands.isDrawn() \
            and self.bollingerBands.belowLowerBandOneBarAgo(previousCandle.low) \
            and self.bollingerBands.bandwidthHasIncreased() 
            

