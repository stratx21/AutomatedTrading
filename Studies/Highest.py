from Studies.study import Study

class Highest(Study):

    def __init__(self, length):
        super().__init__()
        self.length = length 
        self.pricesQueue = []

    # values is set at the same pace as the candles 
    # - this is to add a whole value, not set it 
    def add(self, price): 
        #is drawn, has enough values, so continue drawing 
        self.pricesQueue.append(price)
        if self.isDrawn():
            self.pricesQueue.pop(0)
            self.values.append(max(self.pricesQueue))
        #still getting values, would not be drawn yet 
        else:
            self.values.append(max(self.pricesQueue))
            if len(self.values) == self.length:
                self.drawn = True   

        
