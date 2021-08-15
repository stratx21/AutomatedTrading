from Strategies.Options.Option import Option

# Trailing Stoploss, Following High by Percentage (of price)

# an addPrice option to check 
class TSFHP(Option):
    IDENTIFIER = "TSFHP"

    # sellOutXPercentage: amount below highest high to sell at, in
    # terms of % of the price
    # example: to create a stoploss of 0.5% below the highest 
    # high, set to 0.5
    def __init__(self, sellOutXPercentage):
        self.sellOutXPercentage = sellOutXPercentage / 100.0 # convert to multiplier from percentage
        self.high = -1 

    def shouldSell(self, strategy, newPrice):
        if strategy.isInPosition():
            if newPrice > self.high:
                self.high = newPrice 

            return newPrice < self.high - self.sellOutXPercentage * newPrice

            # TODO include if shouldSell only called while inPosition is true
            # if shouldSell:
            #     self.high = -1 
            # return shouldSell 

        # not in position 
        self.high = -1 
            
        return False 