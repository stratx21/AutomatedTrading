from time import time
import tkinter as tk 
import tkinter.filedialog as filedialog
import Strategies.StrategyCreator as StrategyCreator
import Terminal.TerminalStrings as TerminalStrings
import csv 
import datetime 
import config 
from multiprocessing import Process 
import time 
from Strategies.Strategy import Strategy 
from mysql.connector import connect, Error 
import gc
from Backtesting.BacktestConfigMediator import getAllOptionsToTest, getStrategyInfoToTest
from DataManagement.Database.StrategyTable import updateStrategyTable
from DataManagement.Database.HistoryTable import updateHistory, getHistory
import config.db_auth_config as db_auth_config
from DataManagement.Database.BacktestTable import insertBacktest, getBacktestResultsDbCount

def calculateAndInsertResult(ticker, stratinfo, filename, datestr, selectHistoryResult, buystart, buystop, optionsStrings, cursor):
    strategies = {}
    for optionsString in optionsStrings:
        strategy = StrategyCreator.create(stratinfo[0], ticker, stratinfo[1], stratinfo[2], stratinfo[3])
        if strategy == None:
            print("error, failed to create strategy for ticker ", ticker, ":", *stratinfo)
        else:
            strategy.batchAddOptionFromString(optionsString)
            strategies[optionsString] = strategy 
        
    
    # add history 
    for historyRow in selectHistoryResult:
        for priceEntry in historyRow:
            for strategy in strategies.values():
                strategy.addPrice(float(priceEntry))

    for strategy in strategies.values():
        strategy.enablePostHistory()
        strategy.disable()

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        first = True 
        lastBid = None 
        lastAsk = None
        for row in reader:
            tmstmp = float(row['Timestamp'])/1000.0
            timestampDatetime = datetime.datetime.fromtimestamp(tmstmp)
            config.simulatingTimeStamp = timestampDatetime
            
            if config.isAfterTime(timestampDatetime, config.AUTOSELL_FOR_CLOSE):
                for strategy in strategies.values():
                    if strategy.inPosition:
                            strategy.sell() # force it to sell at EOD
            
            
            if config.withinBuyingTimeConstraint(buystart, buystop):
                if first:
                    first = False 
                    # NOTE start of a new day
            else:
                if not first:
                    first = True 
                    # NOTE reached end of day 
                    
                    for strategy in strategies.values():
                        if strategy.inPosition:
                            strategy.sell() # force it to sell at EOD
                    #print("profit so far on day: " + str(strategy.profitSoFar))
                    splt = filename.split('/')
                    lastpart = splt[len(splt)-1]


            if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                lastBid = float(row['Bid'])
                for strategy in strategies.values():
                    strategy.setLastBid(lastBid)
            if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                lastAsk = float(row['Ask'])
                for strategy in strategies.values(): 
                    strategy.setLastAsk(lastAsk)

            if ticker not in config.TICKERS_TO_AVG_BA and ticker not in config.TICKERS_TO_USE_ASK:
                if 'Last' in row.keys() and len(row['Last']) > 0:
                    for strategy in strategies.values():
                        strategy.addPrice(float(row['Last']))
            elif ticker in config.TICKERS_TO_USE_ASK:
                # use the ask 
                if lastAsk != None:
                    for strategy in strategies.values(): 
                        strategy.addPrice(lastAsk)
            else: # ticker is in avg BA list 

                if lastBid != None and lastAsk != None:
                    for strategy in strategies.values():
                        strategy.addPrice((lastAsk + lastBid)/2.0)
        del reader
        del first
        del lastBid 
        del lastAsk 
        gc.collect()

    # add last entry for total data per each day, looping has finished 
    for strategy in strategies.values():
        if strategy.inPosition:
            strategy.sell() # force it to sell at EOD
    
    for strategyKey in strategies.keys(): 
        insertBacktest(cursor, ticker, stratinfo, strategyKey, datestr, strategies)
    
    # connection.commit()

    for strategy in strategies.values():
        del strategy 
    gc.collect()




def runProcess(filenames, optionsStrings, strategies, ticker):
    totalRuns = len(filenames) * len(strategies) * len(optionsStrings)
    config.simulating = True
    Strategy.outputEnabled = False 
    buystart = config.getBuyStart(ticker)
    buystop = config.getBuyStop(ticker)

    print("started process for ticker", ticker, "- runs to process:", str(totalRuns))

    entriesAlreadyExistedCount = 0
    entriesAddedCount = 0

    try:
        with connect(
            host=db_auth_config.host,
            user=db_auth_config.user,
            password=db_auth_config.password,
            database=db_auth_config.database
        ) as connection:
            with connection.cursor() as cursor:
                for filename in filenames:
                    splt = filename.split('/')
                    lastpart = splt[len(splt)-1]
                    datestr = lastpart[lastpart.find('__')+2:lastpart.find('.csv')]

                    # get history 
                    selectHistoryResult = getHistory(filename, cursor, ticker)

                    for stratinfo in strategies:
                        optStringsToTest = []

                        for optionsString in optionsStrings:
                            selectLen = getBacktestResultsDbCount(cursor, ticker, stratinfo, optionsString, datestr)
                            if selectLen == 0:
                                # strategy with options not in DB - set up to add.
                                optStringsToTest.append(optionsString)
                        
                        if len(optStringsToTest) > 0:
                            # Has no results : calculate and insert entry 

                            calculateAndInsertResult(ticker, stratinfo, filename, datestr, selectHistoryResult, buystart, buystop, optStringsToTest, cursor)
                            connection.commit()
                            entriesAddedCount += len(optStringsToTest)
                            entriesAlreadyExistedCount += len(optionsStrings) - len(optStringsToTest)

                        else:
                            entriesAlreadyExistedCount += len(optionsStrings)

                        # del selectResult 
                        # gc.collect()

                    del selectHistoryResult
                    gc.collect()
                            

    except Error as e:
        print("error with db: ", e)


    print("done testing with streamed tick data for ", ticker, ".")
    print(str(entriesAddedCount), "entries added,", str(entriesAlreadyExistedCount), "entries already existed.")


def run():
    root = tk.Tk()
    filenames = filedialog.askopenfilenames(parent=root, title='Choose a file')
    root.withdraw() # make window go away 

    # strategy info listing 
    strategies = getStrategyInfoToTest() 
    optionsStrings = getAllOptionsToTest()

    
    print("total strategies: " + str(len(strategies)))

    config.simulating = True # enforces simulation logging and network standards 

    print() # print blank line before running, so when it removes a line it will not remove
                # the input section

    totalRuns = len(filenames) * len(strategies) * len(optionsStrings)
    filesPerTicker = {}

    for filename in filenames:
        splt = filename.split('/')
        lastpart = splt[len(splt)-1]
        ticker = lastpart[(lastpart.find('_')+1):lastpart.find('__')]

        if ticker not in filesPerTicker:
            filesPerTicker[ticker] = []

        filesPerTicker[ticker].append(filename)

    # start_timer = time.time()
    # print("start time: ", start_timer)

    # update history
    print("updating history...")
    updateHistory(filesPerTicker.keys())

    print("\n========================================\n")
    print("updating strategy permutations...")
    updateStrategyTable()

    print("\n========================================\n")
    print("total runs to process: ", str(totalRuns))

    for ticker in filesPerTicker.keys():
        Process(target=runProcess, args = (filesPerTicker[ticker], optionsStrings, strategies, ticker)).start()
        
        #runProcess(filesPerTicker[ticker], strategies, ticker)

    # print("finished! elapsed time: ", (time.time()-start_timer))

    
            






if __name__ == "__main__":
    run()