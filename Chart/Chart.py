

#has only finished candles in it 
# - new candle held in RangeStock
# until it finishes 
class Chart:

    def __init__(self, studies = [], newCandleEventListener = None, onNewCandleEventOptListener = None):
        self.studies = studies
        self.onNewCandleEventListener = newCandleEventListener
        self.onNewCandleEventOptListener = onNewCandleEventOptListener
        self.candleList = []

    def add(self, newCandle):
        self.candleList.append(newCandle)
        if self.onNewCandleEventListener != None:
            self.onNewCandleEventListener(newCandle)
        if self.onNewCandleEventOptListener != None:
            self.onNewCandleEventOptListener(newCandle)

    def getBarAt(self, index):
        return None if (index < 0 or index >= self.getSizeInCandles()) else self.candleList[index]

    def getSizeInCandles(self):
        return len(self.candleList)

    def setNewCandleListener(self, listener):
        self.onNewCandleEventListener = listener

    def setNewOptCandleListener(self, listener):
        self.onNewCandleEventOptListener = listener 

    def addStudy(self, study):
        self.studies.append(study)

    def getStudies(self):
        return self.studies 

    def getLastCandle(self):
        return self.getBarAt(len(self.candleList)-1)