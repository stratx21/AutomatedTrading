##########
#STOCK has CHART, 
#   CHART has CANDLES
# 
# smallest to largest: 



class Candle:

    def __init__(self, initPrice):
        self.high = self.low = self.open = self.close = initPrice

    def setHighAndCloseToMax(self, maxSize):
        self.high = self.close = self.low + maxSize 

    def setLowAndCloseToMax(self, maxSize):
        self.low = self.close = self.high - maxSize

    def setHighAndCloseToMaxRenko(self, maxSize):
        self.high = self.close = self.open + maxSize 

    def setLowAndCloseToMaxRenko(self, maxSize):
        self.low = self.close = self.open - maxSize

    def setHighAndClose(self, newPrice):
        self.high = self.close = newPrice

    def setLowAndClose(self, newPrice):
        self.low = self.close = newPrice

    def getLowIgnoringWicks(self):
        return self.close if self.close <= self.open else self.open 

    def getHighIgnoringWicks(self):
        return self.close if self.close >= self.open else self.open 