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
        self.selectHistoryResult = selectHistoryResult
        self.buystart = buystart 
        self.buystop = buystop

        self.fileData = []
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.fileData.append(row)


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
                strategy.addPrice(float(priceEntry))

        strategy.enablePostHistory()
        strategy.disable() # so it will not send orders - simulate 
        
        first = True 
        lastBid = None 
        lastAsk = None
        for row in self.fileData:
            tmstmp = float(row['Timestamp'])/1000.0
            timestampDatetime = datetime.datetime.fromtimestamp(tmstmp)
            config.simulatingTimeStamp = timestampDatetime
            
            if config.isAfterTime(timestampDatetime, config.AUTOSELL_FOR_CLOSE):
                if strategy.inPosition:
                    strategy.sell() # force it to sell at EOD
            
            
            if config.withinBuyingTimeConstraint(self.buystart, self.buystop):
                if first:
                    first = False 
                    # NOTE start of a new day
            else:
                if not first:
                    first = True 
                    # NOTE reached end of day 
                    if strategy.inPosition:
                        strategy.sell() # force it to sell at EOD

            if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                lastBid = float(row['Bid'])
                strategy.setLastBid(lastBid)
            if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                lastAsk = float(row['Ask'])
                strategy.setLastAsk(lastAsk)

            # TODO fix this order
            if self.ticker not in config.TICKERS_TO_AVG_BA and self.ticker not in config.TICKERS_TO_USE_ASK:
                if 'Last' in row.keys() and len(row['Last']) > 0:
                    strategy.addPrice(float(row['Last']))
            elif self.ticker in config.TICKERS_TO_USE_ASK:
                # use the ask 
                if lastAsk != None:
                    strategy.addPrice(lastAsk)
            else: # ticker is in avg BA list 
                if lastBid != None and lastAsk != None:
                    strategy.addPrice((lastAsk + lastBid)/2.0)

        # add last entry for total data per each day, looping has finished 
        if strategy.inPosition:
            strategy.sell() # force it to sell at EOD
        
        insertBacktest(cursor, self.ticker, stratinfo, self.datestr, strategy.getProfitSoFar(), strategy.getTradesSoFar())
