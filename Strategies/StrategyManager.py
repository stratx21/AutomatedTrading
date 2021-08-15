

#Strategy Manager manages the different strategies that have been
# added to run. 
# : StrategyManager holds all the strategy process managers 

from Strategies.StrategyProcessManager import StrategyProcessManager
import Terminal.TerminalStrings as TerminalStrings
import json 

class StrategyManager:
    strategyProcessManagers = {}

    def addStrategy(self, strategyName, strategyTicker, strategyAggregation, optionalArg1 = None, optionalArg2 = None):
        # TODO spin off process for StrategyProcessManager 
        self.strategyProcessManagers[strategyTicker] = StrategyProcessManager(strategyName, strategyTicker, strategyAggregation, optionalArg1, optionalArg2) 

    def sendPrice(self, ticker, lastPrice, bid = None, ask = None):
        if ticker in self.strategyProcessManagers.keys():
            self.strategyProcessManagers[ticker].sendPriceUpdate(json.dumps({"last": lastPrice, "bid": "None" if bid == None else bid, "ask": "None" if ask == None else ask}))

    def terminateAll(self):
        for spm in self.strategyProcessManagers:
            spm.terminateStrategyProcess()

    def sendMessageToTicker(self, ticker, message):
        if ticker in self.strategyProcessManagers:
            self.strategyProcessManagers[ticker].sendCustomMessage(message)
        else: 
            print(TerminalStrings.ERROR + " StrategyManager.sendMessageToTicker: error, ticker \"" + ticker + "\" was not found.")
