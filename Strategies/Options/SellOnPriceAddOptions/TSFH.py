from Strategies.Options.Option import Option

# Trailing Stoploss, Following High

# an addPrice option to check 
class TSFH(Option):
    IDENTIFIER = "TSFH"

    # sellOutX: amount below highest high to sell at
    # example: to create a stoploss of 40 cents below the highest 
    # high, set to 0.40 
    def __init__(self, sellOutX):
        self.sellOutX = sellOutX / 100.0 # convert to cents from $
        self.high = -1 

    def shouldSell(self, strategy, newPrice):
        if strategy.isInPosition():
            if newPrice > self.high:
                self.high = newPrice 

            return newPrice < self.high - self.sellOutX

            # TODO include if shouldSell only called while inPosition is true
            # if shouldSell:
            #     self.high = -1 
            # return shouldSell 

        # not in position 
        self.high = -1 
            
        return False 