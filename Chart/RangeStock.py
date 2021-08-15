import Terminal.TerminalStrings as TerminalStrings
from Chart.Chart import Chart 
from Chart.Candle import Candle
from Chart.StockChartParent import StockChartParent




class RangeStock(StockChartParent):

    # create stock Range chart, starting from the start price 
    def __init__(self, ticker, aggregationInTicks):
        super().__init__(ticker)

        self.aggregationInTicks = int(aggregationInTicks)
        self.aggregationInCents = self.aggregationInTicks / 100.0
        self.init = False 


    #update chart with new price 
    #@Override
    def addQuotePrice(self, newPrice):
        if not self.init:
            #init with first price, start so candles are even. (they will line up)
            self.init = True 
            newPrice = round(newPrice, 2)

            # force the start to be evenly divisible by the aggregation
            self.currentCandle = Candle(int(newPrice/self.aggregationInCents)*self.aggregationInCents)
            self.addQuotePrice(newPrice)
            
        else:
            if self.currentCandle.close < newPrice:
                #while too long for current candle - make a new candle 
                while newPrice - self.currentCandle.low >= self.aggregationInCents:
                    self.currentCandle.setHighAndCloseToMax(self.aggregationInCents)
                    lastClose = self.currentCandle.close
                    self.chart.add(self.currentCandle)
                    self.currentCandle = Candle(lastClose)

                #next price within acceptable range for current candle 
                if newPrice > self.currentCandle.high:
                    self.currentCandle.setHighAndClose(newPrice)
                else:
                    self.currentCandle.close = newPrice

            elif self.currentCandle.close > newPrice: 
                #while too long for current candle - make a new candle 
                while self.currentCandle.high - newPrice >= self.aggregationInCents:
                    self.currentCandle.setLowAndCloseToMax(self.aggregationInCents)
                    lastClose = self.currentCandle.close
                    self.chart.add(self.currentCandle)
                    self.currentCandle = Candle(lastClose)

                #next price within acceptable range for current candle 
                if newPrice < self.currentCandle.low:
                    self.currentCandle.setLowAndClose(newPrice)
                else:
                    self.currentCandle.close = newPrice



