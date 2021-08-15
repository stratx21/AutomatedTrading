import Terminal.TerminalStrings as TerminalStrings
from Chart.Chart import Chart 
from Chart.Candle import Candle
from Chart.StockChartParent import StockChartParent

class RenkoStock(StockChartParent):

    # create stock Renko chart, starting from the start price 
    def __init__(self, ticker, aggregationInTicks):
        super().__init__(ticker)

        self.aggregationInTicks = int(aggregationInTicks)
        self.aggregationInCents = self.aggregationInTicks / 100.0
        self.init = False 
        self.lastBarGreen = None 
    
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
            if self.currentCandle.close < newPrice: # gone up
                #while too long for current candle - make a new green candle 
                while newPrice - self.currentCandle.open >= self.aggregationInCents * (1 if self.lastBarGreen else 2):
                    self.currentCandle.setHighAndCloseToMaxRenko(self.aggregationInCents * (1 if self.lastBarGreen else 2))
                    lastClose = self.currentCandle.close
                    self.chart.add(self.currentCandle)
                    self.currentCandle = Candle(lastClose)
                    self.lastBarGreen = True 

                #next price within acceptable range for current candle 
                if newPrice > self.currentCandle.high:
                    self.currentCandle.setHighAndClose(newPrice)
                else:
                    self.currentCandle.close = newPrice

            elif self.currentCandle.close > newPrice: # gone down 
                #while too long for current candle - make a new red candle 
                while self.currentCandle.open - newPrice >= self.aggregationInCents * (1 if (not self.lastBarGreen) else 2):
                    self.currentCandle.setLowAndCloseToMaxRenko(self.aggregationInCents * (1 if (not self.lastBarGreen) else 2))
                    lastClose = self.currentCandle.close
                    self.chart.add(self.currentCandle)
                    self.currentCandle = Candle(lastClose)
                    self.lastBarGreen = False 

                #next price within acceptable range for current candle 
                if newPrice < self.currentCandle.low:
                    self.currentCandle.setLowAndClose(newPrice)
                else:
                    self.currentCandle.close = newPrice

