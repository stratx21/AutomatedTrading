from Studies.study import Study
from queue import Queue

class ClosePrice(Study):
    def add(self, price): 
        self.values.append(price)
        # self.drawn = True 

    def __init__(self):
        super().__init__()
