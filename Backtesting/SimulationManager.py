import csv
import datetime
from DataManagement.Database.BacktestTable import insertBacktest
import Strategies.StrategyCreator as StrategyCreator
import config 


class SimulationManager:

    def __init__(self, ticker, filename, datestr, selectHistoryResult, buystart, buystop):
        self.ticker = ticker
        self.filename = filename 
        self.datestr = datestr 
        self.buystart = buystart 
        self.buystop = buystop

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
                row['Timestamp'] = datetime.datetime.fromtimestamp(float(row['Timestamp'])/1000.0)

                if 'Last' in row.keys() and len(row['Last']) > 0:
                    row['Last'] = float(row['Last'])
                else:
                    row['Last'] = None 

                if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                    row['Bid'] = float(row['Bid'])
                else:
                    row['Bid'] = None 

                if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                    row['Ask'] = float(row['Ask'])
                else:
                    row['Ask'] = None 
                
                self.fileData.append(row)

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
        if last:
            strategy.addPrice(last)

    def addAskAsPrice(self, strategy, last):
        # no check for ask is None, assuming since first data entry includes all data (includes bid and ask)
        strategy.addPrice(strategy.getLastAsk())

    def addAvgBaAsPrice(self, strategy, last):
        # no check for ask is None, assuming since first data entry includes all data (includes bid and ask)
        strategy.addPrice((strategy.getLastAsk() + strategy.getLastBid())/2.0)

    ####################################################################


    def calculateAndInsertResult(self, stratinfo, cursor):
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
        
        # add history 
        for historyRow in self.selectHistoryResult:
            for priceEntry in historyRow:
                strategy.addPrice(priceEntry)

        strategy.enablePostHistory()
        strategy.disable() # so it will not send orders - simulate 

        lastBid = None 
        lastAsk = None 
        for row in self.fileData:
            # tmstmp = float(row['Timestamp'])/1000.0
            timestampDatetime = row['Timestamp'] # datetime.datetime.fromtimestamp(tmstmp)
            config.simulatingTimeStamp = timestampDatetime
            
            if strategy.isInPosition() and config.isAfterTime(timestampDatetime, config.AUTOSELL_FOR_CLOSE):
                strategy.sell() # force it to sell at EOD
            
            
            # if config.withinBuyingTimeConstraint(self.buystart, self.buystop):
            #     if first:
            #         first = False 
            #         # NOTE start of a new day
            # else:
            #     if not first:
            #         first = True 
            #         # NOTE reached end of day 
            #         if strategy.inPosition:
            #             strategy.sell() # force it to sell at EOD

            if row['Bid']:
                strategy.setLastBid(lastBid)
            if row['Ask']:
                strategy.setLastAsk(lastAsk)

            self.functionForAddingPrice(strategy, row['Last'])
            

        # check if still in position after tick stream file data is done  
        if strategy.inPosition:
            strategy.sell() # force it to sell in case the file did not have EOD data
        
        insertBacktest(cursor, self.ticker, stratinfo, self.datestr, strategy.getProfitSoFar(), strategy.getTradesSoFar())
