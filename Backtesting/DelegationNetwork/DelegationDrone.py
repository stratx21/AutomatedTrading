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


def runDrone(strategies, filename, ticker):
    # filename is the file itself without directories 
    datestr = filename[filename.find('__')+2:filename.find('.csv')]

    # now append directory: 
    filename = db_auth_config.streamRecordsDirectory + filename 

    config.simulating = True
    Strategy.outputEnabled = False 

    try:
        with connect(
            host=db_auth_config.host,
            user=db_auth_config.userDB,
            password=db_auth_config.passwordDB,
            database=db_auth_config.database
        ) as connection, connection.cursor() as cursor:
            # get history 
            selectHistoryResult = getHistory(filename, cursor, ticker)

            simulationManager = SimulationManager(ticker, filename, datestr, selectHistoryResult, BacktestBatchInsertManager(connection, cursor))

            for stratinfo in strategies:
                simulationManager.calculateAndInsertResult(stratinfo)

            # commit after to catch any leftovers that were processed
            simulationManager.finish()


    except Error as e:
        print("error with db: ", e)




    