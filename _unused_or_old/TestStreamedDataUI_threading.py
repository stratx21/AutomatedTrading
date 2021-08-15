import tkinter as tk 
import tkinter.filedialog as filedialog
import Strategies.StrategyCreator as StrategyCreator
import Terminal.TerminalStrings as TerminalStrings
import csv 
from datetime import datetime 
import config 
import ThreadPoolExecutorPlus
import threading
from filelock import Timeout, FileLock
from multiprocessing import Process
import time 

def getKey(entry):
    return entry['profit'] * 1.0 / entry['trades']

def runPerStrategy(filenames, stratinfo, orderedTotals, runCount, runLock, fileLock, totalRuns):
    profitForThisStratAndTicker = 0.0
    tradesForThisStratAndTicker = 0
    lastTicker = None 
    # totalRuns = len(filenames)
    for filename in filenames:
        #print ("\033[A                             \033[A") # remove previous line 
        #print("Running stream data test "+str(runCount)+"/"+str(totalRuns))
        # with runLock:
        #     runCount += 1
        splt = filename.split('/')
        lastpart = splt[len(splt)-1]
        ticker = lastpart[(lastpart.find('_')+1):lastpart.find('__')]
        buystart = config.getBuyStart(ticker)
        buystop = config.getBuyStop(ticker)
        if ticker != lastTicker:
            # add an extra cent per trade of error 
            # require a positive profit to show the total
            if profitForThisStratAndTicker - tradesForThisStratAndTicker/100.0 > 0:
            
                rw = {
                    'ticker': lastTicker,
                    'stratName': stratinfo[0],
                    'aggregation': stratinfo[1],
                    'param1': stratinfo[2] if stratinfo[2] != None else "None",
                    'param2': stratinfo[3] if stratinfo[3] != None else "None",
                    'datafile': "TOTAL",
                    'day': day,
                    'profit': profitForThisStratAndTicker,
                    'trades': tradesForThisStratAndTicker
                }
                # with fileLock:
                #     writer.writerow(rw)
                if lastTicker not in orderedTotals:
                    orderedTotals[lastTicker] = []
                orderedTotals[lastTicker].append(rw)

            profitForThisStratAndTicker = 0.0 
            tradesForThisStratAndTicker = 0
            lastTicker = ticker 

        strategy = StrategyCreator.create(stratinfo[0], ticker, stratinfo[1], stratinfo[2], stratinfo[3])
        strategy.enablePostHistory()
        strategy.disable()

        day = 1
        with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                first = True 
                lastTime = None 
                lastBid = None 
                lastAsk = None
                for row in reader:
                    tmstmp = float(row['Timestamp'])/1000.0
                    timestampDatetime = datetime.fromtimestamp(tmstmp)
                    lastTime = timestampDatetime
                    config.simulatingTimeStamp = timestampDatetime
                    
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
                            #print("profit so far on day: " + str(strategy.profitSoFar))

                            #NOTE: does not write 
                            # writer.writerow({
                            #     'ticker': ticker,
                            #     'stratName': stratinfo[0],
                            #     'aggregation': stratinfo[1],
                            #     'param1': stratinfo[2] if stratinfo[2] != None else "None",
                            #     'param2': stratinfo[3] if stratinfo[3] != None else "None",
                            #     'datafile': lastpart,
                            #     'day': day,
                            #     'profit': strategy.profitSoFar,
                            #     'trades': strategy.tradesMade
                            # })
                            profitForThisStratAndTicker += strategy.profitSoFar
                            tradesForThisStratAndTicker += strategy.tradesMade
                            day += 1

                    if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                        lastBid = float(row['Bid'])
                        strategy.setLastBid(lastBid)
                    if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                        lastAsk = float(row['Ask'])
                        strategy.setLastAsk(lastAsk)

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
        pass

    # add last after finishes
    if profitForThisStratAndTicker - tradesForThisStratAndTicker/100.0 > 0:
        rw = {
            'ticker': lastTicker,
            'stratName': stratinfo[0],
            'aggregation': stratinfo[1],
            'param1': stratinfo[2] if stratinfo[2] != None else "None",
            'param2': stratinfo[3] if stratinfo[3] != None else "None",
            'datafile': "TOTAL",
            'day': "TOTAL",
            'profit': profitForThisStratAndTicker,
            'trades': tradesForThisStratAndTicker
        }
        # with fileLock:
        #     writer.writerow(rw)
        if ticker not in orderedTotals:
            orderedTotals[ticker] = []
        orderedTotals[ticker].append(rw)

    profitForThisStratAndTicker = 0.0 
    tradesForThisStratAndTicker = 0
    lastTicker = ticker 

def run():
    root = tk.Tk()
    filenames = filedialog.askopenfilenames(parent=root, title='Choose a file')

    # print("files: ", files[0])

    strategies = [] 

    with open("strategiesToTest.config") as f:
        strategyConfigLines = f.read().splitlines()

    for line in strategyConfigLines:
        inputs = line.split()
        stratName = inputs[1].upper()
        aggregation = inputs[0]
        if not StrategyCreator.isStrategyName(stratName):
            print(TerminalStrings.ERROR + " strategy \""+stratName+"\" not found! ")
        else: 
            if len(inputs) < 3:
                strategies.append((stratName, aggregation, None, None))
            elif len(inputs) < 4: 
                strategies.append((stratName, aggregation, inputs[2], None))
            else: 
                strategies.append((stratName, aggregation, inputs[2], inputs[3]))

    config.simulating = True

    print() # print blank line before running, so when it removes a line it will not remove
                # the input section

    orderedTotals = {}
    start_timer = time.time()
    print("start time: ", start_timer)

    with open('Records/TestResults.csv', 'w', newline='') as csvfile:
        fieldnames = ['ticker', 'stratName', 'aggregation', 'param1', 'param2', 
                        'datafile', 'day', 'profit', 'trades']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        pass # open as new file 

    totalRuns = len(filenames) * len(strategies)
    runCount = 0
    runLock = FileLock("backtest1.lock")
    fileLock = FileLock("backtest2.lock")

    with ThreadPoolExecutorPlus.ThreadPoolExecutor(max_workers=75) as executor:
        executor.set_daemon_opts(min_workers=1, max_workers=75)
        for stratinfo in strategies:
            executor.submit(runPerStrategy, filenames, stratinfo, orderedTotals, runCount, runLock, fileLock, totalRuns)
            # Process(target=runPerStrategy, args=(filenames, stratinfo, orderedTotals, runCount, runLock, fileLock, totalRuns)).start()

    print("finished! elapsed time: ", (time.time()-start_timer))

    print("done testing with streamed tick data.")

    print("processing results...")
    with open('Records/TestResultsSummary.csv', 'w', newline='') as csvfile:
        fieldnames = ['ticker', 'stratName', 'aggregation', 'param1', 'param2', 
            'datafile', 'day', 'profit', 'trades', 'ProfitPerTrade']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for ticker2 in orderedTotals.keys():
            sorted_list = orderedTotals[ticker2]
            sorted_list.sort(key=getKey)
            for dict in sorted_list:
                dict['ProfitPerTrade'] = getKey(dict)
                writer.writerow(dict)
            






if __name__ == "__main__":
    run()