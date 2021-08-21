from Strategies.Options.Option import Option

# an on attempted buy option
class StopAtPercentLossSum(Option):
    IDENTIFIER = "stopAtPercentLossSum"

    def __init__(self, maxPercentLoss):
        self.maxPercentLoss = maxPercentLoss
        self.totalLosses = 0.00
        self.lastProfit = 0.00

    def isOk(self, strategy):
        newProfit = strategy.getProfitSoFar()
        # if the option is being added late, not at the beginning of trading, 
        #   this will count an initial total negative loss when the opt is 
        #   added as one loss to add.
        if newProfit != self.lastProfit:
            if newProfit < self.lastProfit:
                self.totalLosses += newProfit - self.lastProfit
            self.lastProfit = newProfit

        return self.totalLosses > strategy.getLastAsk() * (self.maxPercentLoss / -100.0)

