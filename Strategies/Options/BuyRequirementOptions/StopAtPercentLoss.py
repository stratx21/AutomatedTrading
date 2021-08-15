from Strategies.Options.Option import Option

# an on attempted buy option
class StopAtPercentLoss(Option):
    IDENTIFIER = "stopAtPercentLoss"

    def __init__(self, maxPercentLoss):
        self.maxPercentLoss = maxPercentLoss

    def isOk(self, strategy):
        return strategy.getProfitSoFar() > strategy.getLastAsk() * (self.maxPercentLoss / -100.0)

