import csv
import datetime
import Strategies.StrategyCreator as StrategyCreator
import config 
import Tools.TimeManagement as TimeManagement
import time 


class SimulationManager:

    # TODO remove buystart and buystop 
    def __init__(self, ticker, filename, datestr, selectHistoryResult, backtestBatchInsertManager):
        self.ticker = ticker
        self.filename = filename 
        self.datestr = datestr 
        self.backtestBatchInsertManager = backtestBatchInsertManager

        # set the history data from DB to be used
        self.selectHistoryResult = []
        for historyRow in selectHistoryResult:
            candleDataFloats = []
            for priceEntry in historyRow:
                candleDataFloats.append(float(priceEntry))
            self.selectHistoryResult.append(candleDataFloats)

        # set the tick stream file data to use for each strategy, and modify for faster access
        self.fileData = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data = {}
                data['Timestamp'] = datetime.datetime.fromtimestamp(float(row['Timestamp'])/1000.0)

                if 'Last' in row.keys() and len(row['Last']) > 0:
                    data['Last'] = float(row['Last'])
                else:
                    data['Last'] = None 

                if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                    data['Bid'] = float(row['Bid'])
                else:
                    data['Bid'] = None 

                if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                    data['Ask'] = float(row['Ask'])
                else:
                    data['Ask'] = None 
                
                self.fileData.append(data)

        # assign the function to use for adding a price to the strategy
        if self.ticker in config.TICKERS_TO_USE_ASK:
            # use the ask 
            self.functionForAddingPrice = self.addAskAsPrice
        elif self.ticker in config.TICKERS_TO_AVG_BA:
            # ticker is in avg BA list 
            self.functionForAddingPrice = self.addAvgBaAsPrice
        else: 
            # is in neither list 
            self.functionForAddingPrice = self.addLastPrice

    ################################################################### 
    # price adding functions: 
    def addLastPrice(self, strategy, last):
        if last != None and last != "":
            strategy.addPrice(float(last))

    def addAskAsPrice(self, strategy, last):
        # no check for ask is None, assuming since first data entry includes all data (includes bid and ask)
        strategy.addPrice(strategy.getLastAsk())

    def addAvgBaAsPrice(self, strategy, last):
        # no check for ask is None, assuming since first data entry includes all data (includes bid and ask)
        strategy.addPrice((strategy.getLastAsk() + strategy.getLastBid())/2.0)

    ####################################################################


    def finish(self):
        self.backtestBatchInsertManager.flush()

    def calculateAndInsertResult(self, stratinfo):
        #              0     1            2       3       4            5
        # stratinfo: (id, name, aggregation, param1, param2, options_str)

        # strategyName, strategyTicker, strategyAggregation, optionalArg1=None, optionalArg2=None
        strategy = StrategyCreator.create(
            stratinfo[1], 
            self.ticker, 
            stratinfo[2], 
            None if stratinfo[3] == "None" else stratinfo[3],
            None if stratinfo[4] == "None" else stratinfo[4])
        if strategy == None:
            print("error, failed to create strategy for ticker ", self.ticker, ":", *stratinfo)
            return
        
        # add opts:
        strategy.batchAddOptionFromString(stratinfo[5])

        # add history 
        for historyRow in self.selectHistoryResult:
            for priceEntry in historyRow:
                strategy.addPrice(priceEntry)

        # if strategy.getProfitSoFar() > 0 or strategy.getTradesSoFar() > 0:
        #     print("Error: profit or trades > 0 right after history in backtest!")

        strategy.enablePostHistory()
        strategy.disable() # so it will not send orders - simulate 

        for row in self.fileData:
            timestampDatetime = row['Timestamp']
            # NOTE: if modifications cause processing multiple strategies at once, 
            #  never have config.simulatingTimeStamp set differently within the same process
            config.simulatingTimeStamp = timestampDatetime

            if strategy.isInPosition() and TimeManagement.pastForceSellEOD():
                strategy.sell() # force it to sell at EOD

            if row['Bid'] != None: 
                strategy.setLastBid(row['Bid'])
            if row['Ask'] != None: 
                strategy.setLastAsk(row['Ask'])

            self.functionForAddingPrice(strategy, row['Last'])

        # check if still in position after tick stream file data is done  
        if strategy.inPosition:
            strategy.sell() # force it to sell in case the file did not have EOD data
        
        self.backtestBatchInsertManager.insert(self.ticker, stratinfo[0], self.datestr, strategy.getProfitSoFar(), strategy.getTradesSoFar())
