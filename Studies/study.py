

class Study():
    def __init__(self):
        self.values = []
        self.drawn = False

    def valueAt(self, index):
        return self.values[index]

    def isDrawn(self):
        return self.drawn

    def getLatestValue(self):
        return self.values[len(self.values)-1]

    def getData(self):
        return self.values

    def dataSize(self):
        return len(self.values)

    def removeLatestValue(self):
        self.values.pop()

    # generalized valid functions, for SMAs EMAs etc: 

    def isValidAtIndex(self, index):
        return self.valueAt(index) != -1 

    def isValid(self, num):
        return num > -1 

    def getSecondToLastValue(self):
        return self.values[len(self.values)-2]