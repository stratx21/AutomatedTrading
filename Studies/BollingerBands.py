from Studies.study import Study 
from Studies.SMA import SMA 
from Studies.ClosePrice import ClosePrice
from statistics import stdev 

class BollingerBands(Study):

    def __init__(self, length, num_dev_down, num_dev_up, trackWidthBarsAgo = -1):
        super().__init__()
        self.length = length 
        self.num_dev_down = num_dev_down
        self.num_dev_up   = num_dev_up

        self.pricesQueue = [] 
        self.trackingWidth = False
        
        if trackWidthBarsAgo > 0:
            self.widthQueue = []
            self.trackingWidth = True 
            self.widthTrackingLength = trackWidthBarsAgo
            self.widthFinishedStarting = False 

        self.midLine = SMA(length)
        self.lowerBand = ClosePrice()
        self.upperBand = ClosePrice()

    def add(self, price):
        self.midLine.add(price)
        self.pricesQueue.append(price)

        if len(self.pricesQueue) == self.length + 1:
            # + 1 so it can pop 
            self.drawn = True 

        if self.isDrawn():
            self.pricesQueue.pop(0)

            midlineVal = self.midLine.getLatestValue()
            sdev = stdev(self.pricesQueue)

            self.lowerBand.add(midlineVal + self.num_dev_down * sdev)
            self.upperBand.add(midlineVal + self.num_dev_up   * sdev)

            # bandwidth tracking: 

            if self.trackingWidth:
                self.widthQueue.append((self.upperBand.getLatestValue() - self.lowerBand.getLatestValue()) / self.midLine.getLatestValue() * 100.0)

                if self.widthFinishedStarting:
                    self.widthQueue.pop(0)
                else:
                    if len(self.widthQueue) == self.widthTrackingLength:
                        self.widthFinishedStarting = True 


            # print("lower band: ", self.lowerBand.getLatestValue(), \
            #     " upper band: ", self.upperBand.getLatestValue(), \
            #     " width: " if self.trackingWidth else "", \
            #         str(self.getLatestBandwidth()) if self.trackingWidth else "")
            


        else:
            self.lowerBand.add(-1)
            self.upperBand.add(-1)

            # since width tracking uses a queue it does not
            #  need dummy values for starting from later data 



    def getLatestBandwidth(self):
        if self.trackingWidth and self.widthFinishedStarting:
            return self.widthQueue[len(self.widthQueue)-1]
        else:
            return None 

    def bandwidthHasIncreased(self):
        return self.trackingWidth \
            and self.widthFinishedStarting \
            and self.widthQueue[0] < self.getLatestBandwidth()


    # NOTE : returns false if not drawn yet 
    def aboveLowerBand(self, price):
        val = self.lowerBand.getLatestValue()
        if val == -1:
            return False 
        return price > val 

    # NOTE : returns false if not drawn yet 
    def belowLowerBand(self, price):
        val = self.lowerBand.getLatestValue()
        if val == -1:
            return False 
        return price < val 

    # NOTE : returns false if not drawn yet 
    def belowLowerBandOneBarAgo(self, price):
        val = self.lowerBand.getSecondToLastValue()
        if val == -1:
            return False 
        return price < val 

    # NOTE : returns false if not drawn yet 
    def aboveUpperBand(self, price):
        val = self.upperBand.getLatestValue()
        if val == -1:
            return False 
        return price > val 

    # NOTE : returns false if not drawn yet 
    def belowUpperBand(self, price):
        val = self.upperBand.getLatestValue()
        if val == -1:
            return False 
        return price < val 
    
    # NOTE : returns false if not drawn yet 
    def aboveUpperBandOneBarAgo(self, price):
        val = self.upperBand.getSecondToLastValue()
        if val == -1:
            return False 
        return price > val 
        
        
    # NOTE : returns false if not drawn yet 
    def aboveMidline(self, price):
        val = self.midLine.getLatestValue()
        if val == -1:
            return False 
        return price > val 
        
    # NOTE : returns false if not drawn yet 
    def belowMidline(self, price):
        val = self.midLine.getLatestValue()
        if val == -1:
            return False 
        return price < val 


    def upperBandIsIncreasing(self):
        return self.upperBand.getLatestValue() > self.upperBand.getSecondToLastValue()

    def lowerBandIsIncreasing(self):
        return self.lowerBand.getLatestValue() > self.lowerBand.getSecondToLastValue()

