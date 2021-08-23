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
import CredentialsConfig.server_auth_config as db_auth_config


def runDrone(strategies, filename, ticker, cursor, connection):
    # filename is the file itself without directories 
    datestr = filename[filename.find('__')+2:filename.find('.csv')]

    # now append directory: 
    if db_auth_config.tempStreamCopiesDirectory != None:
        filename = db_auth_config.tempStreamCopiesDirectory + filename 
    else:
        filename = db_auth_config.streamRecordsDirectory + filename

    config.simulating = True
    Strategy.outputEnabled = False 

    # get history 
    selectHistoryResult = getHistory(filename, cursor, ticker)

    simulationManager = SimulationManager(ticker, filename, datestr, selectHistoryResult, BacktestBatchInsertManager(connection, cursor))

    for stratinfo in strategies:
        simulationManager.calculateAndInsertResult(stratinfo)

    # commit after to catch any leftovers that were processed
    simulationManager.finish()


    




    