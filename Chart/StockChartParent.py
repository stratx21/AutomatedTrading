import Terminal.TerminalStrings as TerminalStrings
from Chart.Chart import Chart 
from Chart.Candle import Candle

class StockChartParent:

    # create stock Range chart, starting from the start price 
    def __init__(self, ticker):
        self.ticker = ticker 
        self.chart = Chart()
        self.currentCandle = None
        

    def setNewCandleListener(self, listener):
        self.chart.setNewCandleListener(listener)

    def setNewOptCandleListener(self, listener):
        self.chart.setNewOptCandleListener(listener)

    # returns the last two finished bars from the chart. Bars are in
    # order of least recent to most recent. [0] is 2 bars ago (second to
    # last finished bar), and [1] is 1 bar ago (last finished bar)
    def getLastTwoBars(self):
        size = self.chart.getSizeInCandles()
        return (None if size < 2 else self.chart.getBarAt(size-2), None if size < 1 else self.chart.getBarAt(size-1))

    def getXBarsAgo(self, x):
        return self.chart.getBarAt(self.chart.getSizeInCandles()-x)

    def getCurrentPrice(self):
        return self.currentCandle.close 

    def getLastBar(self):
        return self.getXBarsAgo(1)

    #update chart with new price 
    def addQuotePrice(self, newPrice):
        #parent will just make a 1 tick chart 
        self.chart.add(Candle(newPrice))

    # big, holding a good bit of data - try not to use 
    #  except one time usages 
    def getAllCandles(self):
        return self.chart.candleList

