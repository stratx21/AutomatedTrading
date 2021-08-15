from Studies.study import Study

class EMA(Study):
    
    def __init__(self, length):
        super().__init__()
        self.length = length 
        self.multiplier = 2 / float(1 + length)
        self.tempSum = 0.00

    # values is set at the same pace as the candles 
    # - this is to add a whole value, not set it 
    def add(self, price): 
        #is drawn, has enough values, so continue drawing 
        if self.isDrawn():
            currentIndex = len(self.values) - self.length
            self.values.append((price - self.values[currentIndex]) * self.multiplier + self.values[currentIndex])
        #still getting values, would not be drawn yet 
        else:
            self.tempSum += price
            #this one allows it to start drawing 
            if len(self.values) + 1 == self.length:
                self.drawn = True
                sma = self.tempSum / self.length
                self.values.append(sma)
                #reset
                self.tempSum = 0.00
            #still in limbo before drawing:
            else:
                #                    (+1 because tempsum has new price) V
                self.values.append(self.tempSum / float(self.dataSize()+1))
