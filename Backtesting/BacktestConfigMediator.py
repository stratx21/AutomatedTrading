
import Strategies.StrategyCreator as StrategyCreator


def getAllOptionsToTest():
    # returns all options strings from config file 
    with open("Backtesting/config/optionsToTest.config") as f: 
        #  get options variations from file 
        return f.read().splitlines()

# returns array of strategies: 
#    (name, aggregation, param1, param2)
def getStrategyInfoToTest():
    strategies = [] 

    with open("Backtesting/config/strategiesToTest.config") as f: #  get strategy variations from file 
        strategyConfigLines = f.read().splitlines()

    for line in strategyConfigLines:
        inputs = line.split()
        stratName = inputs[1].upper()
        aggregation = inputs[0]
        if not StrategyCreator.isStrategyName(stratName):
            print(TerminalStrings.ERROR, "strategy \"" + stratName + "\" not found! ")
        else: 
            if len(inputs) < 3:
                strategies.append((stratName, aggregation, None, None))
            elif len(inputs) < 4: 
                strategies.append((stratName, aggregation, inputs[2], None))
            else: 
                strategies.append((stratName, aggregation, inputs[2], inputs[3]))

    return strategies 

