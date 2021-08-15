from Studies.study import Study
from queue import Queue

class SMA(Study):
    
    def __init__(self, length):
        super().__init__()
        self.length = length 
        self.pricesQueue = []
        self.tempSum = 0.00

    # values is set at the same pace as the candles 
    # - this is to add a whole value, not set it 
    def add(self, price): 
        #is drawn, has enough values, so continue drawing 
        if self.isDrawn():
            # sum = sum of last [length] bars (by removing price from [length] bars ago)
            self.tempSum = self.tempSum + price - self.pricesQueue.pop(0)
            self.values.append(self.tempSum / self.length)

        #still getting values, would not be drawn yet 
        else:
            self.tempSum = self.tempSum + price
            #this one allows it to start drawing 
            if len(self.values) + 1 == self.length:
                self.drawn = True
                sma = self.tempSum / self.length
                self.values.append(sma)
            #still in limbo before drawing:
            else:
                self.values.append(-1)

        self.pricesQueue.append(price)  

    # NOTE : returns false if SMA is not drawn yet too 
    def priceIsAbove(self, price):
        val = self.getLatestValue()
        if val == -1:
            return False 
        return price > val 

    # positive velocity 
    def isGreen(self):
        return self.getLatestValue() > self.getSecondToLastValue()








    def isConfirmation(self, candle):
        return self.isDrawn() and candle.open > self.getLatestValue()

    # sma is drawn and one of the two:
    # one: is red bar and open < SMA 
    # two: is green bar and close < SMA 
    def isOriginalValidation(self, candle):
        return self.isDrawn() \
            and ((candle.open < candle.close and candle.open < self.getLatestValue()) \
                or (candle.open <= candle.close and candle.close < self.getLatestValue()))

    # sma is drawn and one of the two:
    # one: is red bar and close < SMA 
    # two: is green bar and close < SMA 
    def isConservativeValidation(self, candle):
        return self.isDrawn() \
            and ((candle.open > candle.close and candle.close < self.getLatestValue()) \
                or (candle.open <= candle.close and candle.close < self.getLatestValue()))


    # this checks with an unfinished candle, not a new candle, and deletes it 
    def checkOriginalValidationWithPrice(self, candleToTestWith):
        self.add(candleToTestWith.close)
        res = self.isOriginalValidation(candleToTestWith)
        self.removeLatestValue()
        return res 

    # this checks with an unfinished candle, not a new candle, and deletes it 
    def checkConservativeValidationWithPrice(self, candleToTestWith):
        self.add(candleToTestWith.close)
        res = self.isConservativeValidation(candleToTestWith)
        self.removeLatestValue()
        return res 
