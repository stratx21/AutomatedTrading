from Strategies.Options.Option import Option

# OCO bracket 

# an addPrice option to check 
class OCO(Option):
    IDENTIFIER = "OCO"

    # sellOutX: amount below highest high to sell at
    # example: to create a stoploss of 40 cents below the highest 
    # high, set to 0.40 
    def __init__(self, stopLossAmount, takeProfitAmount):
        self.stopLossAmount = stopLossAmount / 100.0 # convert to cents from $
        self.takeProfitAmount = takeProfitAmount / 100.0 # convert to cents from $

    def shouldSell(self, strategy, newPrice):
        if strategy.isInPosition(): 
            return newPrice < strategy.getBoughtPrice() - self.stopLossAmount \
                or newPrice > strategy.getBoughtPrice() + self.takeProfitAmount
            
        return False 