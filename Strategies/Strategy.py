

from Strategies.Options.OptionManager import OptionManager
import Terminal.TerminalStrings as TerminalStrings
import Network.Orders as Orders
import Strategies.StrategyRecordWriter as StrategyRecordWriter
import config 
from UI.ProcessLoggingWindow import ProcessLogWindowManager
from Terminal import TerminalTools
import datetime
import threading 

# abstract 
class Strategy:
    NAME = "STRATEGY"
    outputEnabled = True

    def __init__(self, ticker, aggregation): 
        self.ticker, self.aggregation = ticker, aggregation
        self.enabled = True
        self.init = False 
        self.quantity = 1
        self.boughtPrice = -1.00
        self.inPosition = False 
        self.historyFinished = False 
        self.profitSoFar = 0
        self.tradesMade = 0
        self.lastBid = -1
        self.lastAsk = -1
        self.uiWindow = None 

        self.buy_start = config.getBuyStart(self.ticker)
        self.buy_stop  = config.getBuyStop(self.ticker)

        self.optionManager = OptionManager()

        # create CSV record file: 
        if not config.simulating or config.csvBacktestLogEnabled:
            self.csvFile = StrategyRecordWriter.createFileStrategy(self.ticker, self.NAME, str(self.aggregation))

        self.initUI(strategyInit=True)

        if not config.simulating:
            # then start timer to sell at EOD 
            now = datetime.datetime.now()
            goOffAt = now.replace(hour = config.AUTOSELL_FOR_CLOSE.hour, minute = config.AUTOSELL_FOR_CLOSE.minute, second=0)
            if now > goOffAt:
                goOffAt = goOffAt + datetime.timedelta(days=1) # fix if starting for next day before midnight 
            if now < goOffAt:
                threading.Timer((goOffAt - now).total_seconds(), self.sellAtEOD).start()


    def initUI(self, arg1 = None, arg2 = None, strategyInit=False):
        if Strategy.getOutputEnabled():
            self.uiWindow = ProcessLogWindowManager(self.ticker, "["+self.ticker+"] "+str(self.aggregation)+" "+self.NAME)

        # TODO should this be included? 
        # TODO I stopped because it can slow down the 
        #  strategy itself, which may cause order issues 
        #  or slowdowns 

        # if not strategyInit:
        #     # load all candles to the output to catch it up:
        #     for candle in self.stock.getAllCandles():
        #         self.uiWindow.writeCandle(candle)

    @staticmethod
    def getOutputEnabled():
        return Strategy.outputEnabled

    def onNewCandle(self, newCandle):
        self.outputCandleData(newCandle)

        prevBar, newBar = self.stock.getLastTwoBars()

        if prevBar != None and newBar != None: # newBar != None implied if prevBar != None 
            if self.inPosition:
                if self.getSellCondition(newBar, prevBar):
                    self.sell()
            else:
                if self.getBuyCondition(newBar, prevBar):
                    self.buy()

    def sellAtEOD(self):
        if self.inPosition:
            if Strategy.getOutputEnabled():
                print(TerminalStrings.STRATEGY + " " + self.ticker + " autoselling : End Of Day")
            self.sell()

    def addOption(self, optChoice, optArgs):
        self.optionManager.addOption(optChoice, optArgs, self)

    # for backtesting purposes for now 
    def batchAddOptionFromString(self, optionsString):
        self.optionManager.batchAddOptionFromString(optionsString, self)

    # manages adding price to record 
    def addPrice(self, price):
        self.stock.addQuotePrice(price)

        if self.optionManager.shouldSellOnPriceAdd(self, price) and self.isInPosition():
            self.sell()

    def outputCandleData(self, candle):
        # TerminalTools.printStrategyNewCandle(self.ticker, candle)
        if self.uiWindow != None:
            self.uiWindow.writeCandle(candle)

    def terminateUI(self):
        if self.uiWindow != None:
            self.uiWindow.terminate()

    def isInPosition(self):
        return self.inPosition

    def getBoughtPrice(self):
        return self.boughtPrice

    def disable(self):
        self.enabled = False 

    def enable(self):
        self.enabled = True 

    def isDisabled(self):
        return not self.enabled

    def isEnabled(self):
        return self.enabled

    def setLastBid(self, newBid):
        self.lastBid = newBid
    
    def getLastBid(self):
        return self.lastBid

    def setLastAsk(self, newAsk):
        self.lastAsk = newAsk
        
    def getLastAsk(self):
        return self.lastAsk

    def getProfitSoFar(self):
        return self.profitSoFar

    def getTradesSoFar(self):
        return self.tradesMade

    def getTicker(self):
        return self.ticker 

    def getAllCandles(self):
        return self.stock.getAllCandles()

    def enablePostHistory(self):
        if Strategy.getOutputEnabled():
            print(TerminalStrings.STRATEGY + " " + self.ticker + " history finished")
            print(TerminalStrings.STRATEGY + " " + self.ticker + " will trade from " + str(self.buy_start) + " - " + str(self.buy_stop))
        if self.uiWindow != None:
            self.uiWindow.writeHistoryFinished(str(self.buy_start), str(self.buy_stop))
        self.historyFinished = True 

    def getCurrentPriceStr(self):
        return self.stock.getCurrentPrice()

    def buy(self):
        # history has been entered and current time is acceptable in time constraint 
        if self.historyFinished and config.withinBuyingTimeConstraint(self.buy_start, self.buy_stop):
            if self.optionManager.isOkToBuy(self):
                if self.isEnabled():
                    Orders.sendBuyMarketOrder(self.ticker, self.quantity)
                self.inPosition = True
                self.boughtPrice = self.getLastAsk()
                if Strategy.getOutputEnabled():
                    print(TerminalStrings.STRATEGY + " " + self.ticker + " " + self.NAME + " " + TerminalStrings.TRADE_NOTIFICATION + (" " if self.enabled else (" "+TerminalStrings.SIMULATED)) + " BUY +" + str(self.quantity) + " " + self.ticker + " at " + "{:.2f}".format(self.boughtPrice))
                if self.uiWindow != None:
                    self.uiWindow.writeBuyNotification(self.boughtPrice, self.quantity, self.isDisabled())

                # add to record CSV
                if not config.simulating or config.csvBacktestLogEnabled:
                    StrategyRecordWriter.addEntryStrategy(self.csvFile, self.isDisabled(), "BUY", self.boughtPrice)
            else:
                if Strategy.getOutputEnabled():
                    print(TerminalStrings.STRATEGY + " " + TerminalStrings.WARNING + " " + self.ticker + " " + self.NAME + " : would have bought. Options disallowed the buy action.")

        # if still entering history, do nothing

    def sell(self):
        if self.historyFinished and config.withinSellingTimeConstraint():
            if self.isEnabled():
                Orders.sendSellMarketOrder(self.ticker, self.quantity)
            profit = self.getLastBid() - self.boughtPrice
            self.inPosition = False 
            if Strategy.getOutputEnabled():
                print(TerminalStrings.STRATEGY + " " + self.ticker + " " + self.NAME + " " + TerminalStrings.TRADE_NOTIFICATION + (" " if self.enabled else (" "+TerminalStrings.SIMULATED)) + " SELL -" + str(self.quantity) + " " + self.ticker + " at " + "{:.2f}".format(self.getLastBid()) + "; diff: " + "{:.2f}".format(profit))
            if self.uiWindow != None:
                self.uiWindow.writeSellNotification(self.getLastBid(), profit, self.quantity, self.isDisabled())

            # add to record CSV 
            if not config.simulating or config.csvBacktestLogEnabled:
                StrategyRecordWriter.addEntryStrategy(self.csvFile, self.isDisabled(), "SELL", self.getLastBid())

            self.profitSoFar += profit
            self.tradesMade += 1
            if Strategy.getOutputEnabled():
                print(TerminalStrings.STRATEGY + " profit so far: " + "{:.2f}".format(self.profitSoFar), " trades made:", self.tradesMade)
            if self.uiWindow != None:
                self.uiWindow.writePLSummary(self.profitSoFar, self.tradesMade)
        
        # if still entering history, do nothing 
