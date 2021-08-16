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
from DataManagement.Database.BacktestTable import insertBacktest
from DataManagement.Database.HistoryTable import updateHistory, getHistory
from DataManagement.Database.StrategyTable import getStrategiesNotProcessed
import CredentialsConfig.db_auth_config as db_auth_config

# TODO create object with this data ? StrategySimulationManager
# TODO idea: store data from file in array, and reuse 
def calculateAndInsertResult(ticker, stratinfo, filename, datestr, selectHistoryResult, buystart, buystop, cursor):
    #              0     1            2       3       4            5
    # stratinfo: (id, name, aggregation, param1, param2, options_str)

    # strategyName, strategyTicker, strategyAggregation, optionalArg1=None, optionalArg2=None
    strategy = StrategyCreator.create(
        stratinfo[1], 
        ticker, 
        stratinfo[2], 
        None if stratinfo[3] == "None" else stratinfo[3],
        None if stratinfo[4] == "None" else stratinfo[4])
    if strategy == None:
        print("error, failed to create strategy for ticker ", ticker, ":", *stratinfo)
        return
    
    # add history 
    for historyRow in selectHistoryResult:
        for priceEntry in historyRow:
            strategy.addPrice(float(priceEntry))

    strategy.enablePostHistory()
    strategy.disable() # so it will not send orders - simulate 

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
                    if strategy.inPosition:
                        strategy.sell() # force it to sell at EOD

            if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                lastBid = float(row['Bid'])
                strategy.setLastBid(lastBid)
            if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                lastAsk = float(row['Ask'])
                strategy.setLastAsk(lastAsk)

            # TODO fix this order
            if ticker not in config.TICKERS_TO_AVG_BA and ticker not in config.TICKERS_TO_USE_ASK:
                if 'Last' in row.keys() and len(row['Last']) > 0:
                    strategy.addPrice(float(row['Last']))
            elif ticker in config.TICKERS_TO_USE_ASK:
                # use the ask 
                if lastAsk != None:
                    strategy.addPrice(lastAsk)
            else: # ticker is in avg BA list 
                if lastBid != None and lastAsk != None:
                    strategy.addPrice((lastAsk + lastBid)/2.0)

    # add last entry for total data per each day, looping has finished 
    if strategy.inPosition:
        strategy.sell() # force it to sell at EOD
    
    insertBacktest(cursor, ticker, stratinfo, datestr, strategy.getProfitSoFar(), strategy.getTradesSoFar())




def runProcess(filenames, ticker):
    config.simulating = True
    Strategy.outputEnabled = False 
    buystart = config.getBuyStart(ticker)
    buystop = config.getBuyStop(ticker)

    start_timer = time.time()
    print("started process for ticker", ticker, "at time", start_timer)

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

                    strategies = getStrategiesNotProcessed(ticker, datestr, cursor)

                    count = 0
                    for stratinfo in strategies:
                        calculateAndInsertResult(ticker, stratinfo, filename, datestr, selectHistoryResult, buystart, buystop, cursor)
                        count += 1
                        if count >= 1000:
                            connection.commit()
                            count = 0

                    connection.commit()
                            

    except Error as e:
        print("error with db: ", e)

    doneTime = time.time()
    print("done testing with streamed tick data for", ticker + ". End time:", doneTime, "elapsed time:", start_timer - doneTime)
    # print(str(entriesAddedCount), "entries added,", str(entriesAlreadyExistedCount), "entries already existed.")


def run():
    root = tk.Tk()
    filenames = filedialog.askopenfilenames(parent=root, title='Choose a file')
    root.withdraw() # make window go away 

    config.simulating = True # enforces simulation logging and network standards 
    filesPerTicker = {} # list of files per ticker

    for filename in filenames:
        splt = filename.split('/')
        lastpart = splt[len(splt)-1]
        ticker = lastpart[(lastpart.find('_')+1):lastpart.find('__')]

        if ticker not in filesPerTicker:
            filesPerTicker[ticker] = []

        filesPerTicker[ticker].append(filename)

    # update history
    print("updating history...")
    updateHistory(filesPerTicker.keys())

    print("\n========================================\n")
    print("Running update backtest results...")

    for ticker in filesPerTicker.keys():
        Process(target=runProcess, args = (filesPerTicker[ticker], ticker)).start()


if __name__ == "__main__":
    run()