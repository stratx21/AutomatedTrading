from Strategies.Options.Option import Option
import Tools.TimeManagement as TimeManagement
from datetime import timedelta

# if it hits a given percent loss, delay the given amount of time 
#   before buying again. This process will loop, so that if the
#   percent loss is met and the delay runs out, it can lose the 
#   percent loss again, and then be disabled for the same time. 

# an on attempted buy option
class StopAtPercentLoss(Option):
    IDENTIFIER = "delayAtPercentLoss"

    def __init__(self, maxPercentLoss, delayInMinutes):
        self.maxPercentLoss = maxPercentLoss
        self.delayInMinutes = delayInMinutes
        self.profitToCompareTo = 0.00
        self.buyingDisabled = False 
        self.canBuyAgainAt = None 

    def isOk(self, strategy):
        # update self.buyingDisabled: 
        if self.buyingDisabled:
            if TimeManagement.currentTimeIsAfter(self.canBuyAgainAt):
                self.enable()
                self.profitToCompareTo = strategy.getProfitSoFar() # can incur another maxPercentLoss again after delay
        else:
            # is currently allowing buying 
            shouldDisableBuying = strategy.getProfitSoFar() <= strategy.getLastAsk() * (self.maxPercentLoss / -100.0) - self.profitToCompareTo 
            if shouldDisableBuying:
                # just became not ok 
                self.disable()

        # then return the current state: 
        return self.buyingDisabled

    def enable(self):
        self.canBuyAgainAt = None
        self.buyingDisabled = False 

    def disable(self):
        self.canBuyAgainAt = TimeManagement.getCurrentTime() + timedelta(minutes=self.delayInMinutes)
        self.buyingDisabled = True 