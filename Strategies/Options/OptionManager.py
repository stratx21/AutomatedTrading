from Terminal import TerminalStrings
from Strategies.Options.BuyRequirementOptions.StopAtPercentLoss import StopAtPercentLoss
from Strategies.Options.BuyRequirementOptions.DelayAtPercentLoss import DelayAtPercentLoss
from Strategies.Options.SellOnPriceAddOptions.TSFH import TSFH
from Strategies.Options.SellOnPriceAddOptions.TSFHP import TSFHP
from Strategies.Options.SellOnPriceAddOptions.OCO import OCO


class OptionManager:

    def __init__(self):
        # name determines when they are checked 
        self.optionsAtBuy = []
        self.sellOnPriceAddOptions = []


    # TODO create strategy stats object that Strategy holds, and pass that instead of strategy ? 
    def addOption(self, optChoice, optArgs, strategy):
        optionAdded = None 

        #########################
        # BuyRequirementOptions: 
        if optChoice == StopAtPercentLoss.IDENTIFIER:
            try:
                optArg1 = optArgs[0]
                optionAdded = StopAtPercentLoss(float(optArg1))
                self.optionsAtBuy.append(optionAdded)
            except ValueError:
                print(TerminalStrings.ERROR + " OPT arg \"" + str(optArg1) + "\" is not a number, is invalid. Not adding OPT.")
                return
            except IndexError:
                print(TerminalStrings.ERROR + " OPT argument missing: first argument of percentage for " + optionAdded.IDENTIFIER)
                return 

        elif optChoice == DelayAtPercentLoss.IDENTIFIER:
            try:
                optArg1 = optArgs[0]
                optArg2 = optArgs[1]
                optionAdded = DelayAtPercentLoss(float(optArg1), int(optArg2))
                self.optionsAtBuy.append(optionAdded)
            except ValueError:
                print(TerminalStrings.ERROR + " OPT arg \"" + str(optArg1) + "\" or \"" + str(optArg2) + "\" is not a number, is invalid. Not adding OPT.")
                return
            except IndexError:
                print(TerminalStrings.ERROR + " OPT argument missing: first argument of percentage for " + optionAdded.IDENTIFIER)
                return 
        
        #########################
        # SellOnPriceAddOptions: 

        elif optChoice == TSFH.IDENTIFIER:
            try:
                optArg1 = optArgs[0]
                optionAdded = TSFH(float(optArg1))
                self.sellOnPriceAddOptions.append(optionAdded)
            except ValueError:
                print(TerminalStrings.ERROR + " OPT arg \"" + str(optArg1) + "\" is not a number, is invalid. Not adding OPT.")
                return
            except IndexError:
                print(TerminalStrings.ERROR + " OPT argument missing: first argument of percentage for " + optionAdded.IDENTIFIER)
                return 

        elif optChoice == TSFHP.IDENTIFIER:
            try:
                optArg1 = optArgs[0]
                optionAdded = TSFHP(float(optArg1))
                self.sellOnPriceAddOptions.append(optionAdded)
            except ValueError:
                print(TerminalStrings.ERROR + " OPT arg \"" + str(optArg1) + "\" is not a number, is invalid. Not adding OPT.")
                return
            except IndexError:
                print(TerminalStrings.ERROR + " OPT argument missing: first argument of percentage for " + optionAdded.IDENTIFIER)
                return 

        elif optChoice == OCO.IDENTIFIER:
            try:
                optArg1 = optArgs[0]
                optArg2 = optArgs[1]
                optionAdded = OCO(float(optArg1), float(optArg2))
                self.sellOnPriceAddOptions.append(optionAdded)
            except ValueError:
                print(TerminalStrings.ERROR + " OPT arg \"" + str(optArg1) + "\" or \"" + str(optArg2) + "\" is not a number, is invalid. Not adding OPT.")
                return
            except IndexError:
                print(TerminalStrings.ERROR + " OPT argument missing: requires two arguments, option type " + optionAdded.IDENTIFIER)
                return 

        
        else: 
            print(TerminalStrings.ERROR + " OPT choice \"" + str(optChoice) + "\" is invalid. Not adding OPT.")

        for candle in strategy.getAllCandles(): # update up to current 
            optionAdded.update(candle)

        if strategy.getOutputEnabled():
            print(TerminalStrings.SYS_MESSAGE + " option " + optChoice + " " + " ".join(optArgs) + " added for " + strategy.getTicker())



    #############################################################
    # condition check functions: 

    def isOkToBuy(self, strategy):
        # is okay to buy unless options are not in ok state 
        for option in self.optionsAtBuy: 
            if not option.isOk(strategy):
                return False 

        return True  

    def shouldSellOnPriceAdd(self, strategy, newPrice):
        # sell if any options say to sell 
        for option in self.sellOnPriceAddOptions:
            if option.shouldSell(strategy, newPrice):
                return True 

        return False 


    ###############################################################
    
    # update: 
    def onNewCandle(self, newCandle):
        # for option in self.optionsAtBuy:
        #     option.update(newCandle)
        pass # TODO is this function needed? 


    # translate from string: 
    def batchAddOptionFromString(self, stringOfOptions, strategy):
        stripped = stringOfOptions.strip() # remove whitespace 
        if stripped != "None" and stripped != "":
            for optionStr in stringOfOptions.split("; "):
                optionInput = optionStr.split() # " "
                optChoice = optionInput.pop(0)
                # optionInput is now the array of args
                self.addOption(optChoice, optionInput, strategy)
