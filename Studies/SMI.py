from Studies.ClosePrice import ClosePrice
from Studies.SMA import SMA
from Studies.EMA import EMA
from Studies.Highest import Highest
from Studies.Lowest import Lowest
from Studies.study import Study

class SMI(Study):

    def __init__(self, overBought = 40.0, overSold = -40, percentDLength = 3, percentKLength = 5):
        super().__init__()
        self.overBought = overBought
        self.overSold = overSold

        self.lowestStudy = Lowest(percentKLength)
        self.highestStudy = Highest(percentKLength)

        # TODO change SMAs back to EMAs

        self.closeTrackerStudy = ClosePrice()
        self.relStudyInner = SMA(percentDLength)
        self.diffStudyInner = SMA(percentDLength)
        self.relStudyOuter = SMA(percentDLength)
        self.diffStudyOuter = SMA(percentDLength)

        self.smi = ClosePrice()
        self.avgsmi = SMA(percentDLength)


    # values is set at the same pace as the candles 
    # - this is to add a whole value, not set it 
    def add(self, newCandle): 
        self.lowestStudy.add(float(newCandle.low))
        self.highestStudy.add(float(newCandle.high))
        self.closeTrackerStudy.add(newCandle.close)

        min_low = self.lowestStudy.getLatestValue()
        max_high = self.highestStudy.getLatestValue()

        self.relStudyInner.add(newCandle.close - (max_high + min_low)/2)
        self.relStudyOuter.add(self.relStudyInner.getLatestValue())
        self.diffStudyInner.add(max_high - min_low)
        self.diffStudyOuter.add(self.diffStudyInner.getLatestValue())

        avgRel = self.relStudyOuter.getLatestValue()
        avgDiff = self.diffStudyOuter.getLatestValue()
        
        #plot
        self.smi.add((avgRel / (avgDiff / 2) * 100) if avgDiff != 0 else 0)

        #plot
        self.avgsmi.add(self.smi.getLatestValue())

        self.drawn = True 



    def getOverbought(self):
        return self.overBought

    def getOversold(self):
        return self.overSold


    def getSMI(self):
        return self.smi 

    def getAvgSMI(self):
        return self.avgsmi
        

    def getSMILatestValue(self):
        return self.smi.getLatestValue()

    def getAvgSMILatestValue(self):
        return self.avgsmi.getLatestValue()

    def getSMIvalueAt(self, index):
        return self.smi.valueAt(index)

    def getAvgSMIvalueAt(self, index):
        return self.avgsmi.valueAt(index)


    #@Override
    def valueAt(self, index):
        return (self.smi.valueAt(index), self.avgsmi.valueAt(index))

    #@Override
    def dataSize(self):
        return self.smi.dataSize()

    #Strategy Help Functions: 

    def isCrossed(self):
        return self.isDrawn() and self.getSMILatestValue() > self.getAvgSMILatestValue()

    def justCrossed(self):
        prevValues = self.valueAt(self.dataSize() - 2)# -1 would be last one for index 
        #is now crossed and last SMI <= last AvgSMI
        return self.isCrossed() and prevValues[0] <= prevValues[1]
