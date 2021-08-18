# from time import time
import tkinter as tk 
import tkinter.filedialog as filedialog
# import Strategies.StrategyCreator as StrategyCreator
# import Terminal.TerminalStrings as TerminalStrings
# import csv 
import datetime 
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


def runProcess(filenames, ticker):
    config.simulating = True
    Strategy.outputEnabled = False 
    buystart = config.getBuyStart(ticker)
    buystop = config.getBuyStop(ticker)

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
                        simulationManager = SimulationManager(ticker, filename, datestr, selectHistoryResult, BacktestBatchInsertManager(connection, cursor))

                        for stratinfo in strategies:
                            simulationManager.calculateAndInsertResult(stratinfo)

                        # commit after to catch any leftovers that were processed
                        simulationManager.finish()
                            

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