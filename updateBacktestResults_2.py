# from time import time
import tkinter as tk 
import tkinter.filedialog as filedialog
# import Strategies.StrategyCreator as StrategyCreator
# import Terminal.TerminalStrings as TerminalStrings
# import csv 
import datetime 
import threading 
import config 
from multiprocessing import Process 
import time 
from Strategies.Strategy import Strategy 
from mysql.connector import connect, Error 
from DataManagement.Database.BacktestTable import BacktestBatchInsertManager
from DataManagement.Database.HistoryTable import updateHistory, getHistory
from DataManagement.Database.StrategyTable import getStrategiesNotProcessed
from Backtesting.SimulationManager import SimulationManager
import CredentialsConfig.db_auth_config as db_auth_config
from numba import jit, cuda

def chonkIt(list, length):
    toreturn = [] 
    for i in range(0, len(list), length):
        toreturn.append(list[i:i + length])
    return toreturn 

@cuda.jit(forceobj=True)
def processStrategiesSubset(strategies, ticker, filename, datestr, selectHistoryResult, connection, cursor):
    config.simulating = True
    Strategy.outputEnabled = False 
    start_timer = time.time()
    print("started process for ticker", ticker, "at time", datetime.datetime.fromtimestamp(start_timer))
    simulationManager = SimulationManager(ticker, filename, datestr, selectHistoryResult, BacktestBatchInsertManager(connection, cursor))

    for stratinfo in strategies:
        simulationManager.calculateAndInsertResult(stratinfo)

    # commit after to catch any leftovers that were processed
    simulationManager.finish()
    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("done testing with streamed tick data for", 
        ticker + ". End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        str(int(elapsedSeconds/3600)) + "h " + str(int((elapsedSeconds/60) % 60)) + "m " + str((elapsedSeconds % 60)) + "s")


def processStrategiesSubsetThread(simulationManager, strategies):
    runadfsmkfm[16, 32](simulationManager, strategies)

@jit(forceobj=True, target="cuda")
def runadfsmkfm(simulationManager, strategies):
    start_timer = time.time()
    print("started process for ticker", simulationManager.ticker, "at time", datetime.datetime.fromtimestamp(start_timer))
    for stratinfo in strategies:
        simulationManager.calculateAndInsertResult(stratinfo)

    # commit after to catch any leftovers that were processed
    simulationManager.finish()
    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("done testing with streamed tick data for", 
        simulationManager.ticker + ". End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        str(int(elapsedSeconds/3600)) + "h " + str(int((elapsedSeconds/60) % 60)) + "m " + str((elapsedSeconds % 60)) + "s")


# @jit(forceobj=True)
def processStrategies(strategies, ticker, filename, datestr, selectHistoryResult):
    started = time.time()
    threads = []
    mgr = SimulationManager(ticker, filename, datestr, selectHistoryResult, BacktestBatchInsertManager(None, None))
    for stratinfoList in chonkIt(strategies, 500):
        # Process(target=processStrategiesSubset, args = (stratinfoList, ticker, filename, datestr, selectHistoryResult, None, None)).start()
        thread = threading.Thread(target=processStrategiesSubsetThread, args = (mgr, stratinfoList))
        thread.start()
        threads.append(thread)
        # processStrategiesSubset(stratinfoList, ticker, filename, datestr, selectHistoryResult, None, None)
    for thread in threads:
        thread.join()
    doneTime = time.time()
    elapsedSeconds = int(doneTime - started)
    print("TOTALLLLLLLLLLLLLLLL done testing with streamed tick data for", 
        ticker + ". End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        str(int(elapsedSeconds/3600)) + "h " + str(int((elapsedSeconds/60) % 60)) + "m " + str((elapsedSeconds % 60)) + "s")


def processFunct(filenames):
    ticker = filenames.pop()
    config.simulating = True
    Strategy.outputEnabled = False 

    start_timer = time.time()
    print("started process for ticker", ticker, "at time", datetime.datetime.fromtimestamp(start_timer))

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

                    if len(strategies) > 0:
                        processStrategies(strategies, ticker, filename, datestr, selectHistoryResult)
                            

    except Error as e:
        print("error with db: ", e)

    doneTime = time.time()
    elapsedSeconds = int(doneTime - start_timer)
    print("done testing with streamed tick data for", 
        ticker + ". End time:", 
        datetime.datetime.fromtimestamp(doneTime), 
        "elapsed time:", 
        str(int(elapsedSeconds/3600)) + "h " + str(int((elapsedSeconds/60) % 60)) + "m " + str((elapsedSeconds % 60)) + "s")
    # print(str(entriesAddedCount), "entries added,", str(entriesAlreadyExistedCount), "entries already existed.")

def runProcess(filenames, ticker):
    filenames.append(ticker)
    processFunct(filenames)

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
        # Process(target=runProcess, args = (filesPerTicker[ticker], ticker)).start()
        runProcess(filesPerTicker[ticker], ticker)


if __name__ == "__main__":
    run()