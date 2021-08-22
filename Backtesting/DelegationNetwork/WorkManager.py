import json
from Tools.ListTools import splitListIntoChonks
from DataManagement.Database.StrategyTable import getStrategiesNotProcessed
from Tools.StringTools import getInfoFromFullFilename, getTickerFromFilename
from DataManagement.Database.HistoryTable import updateHistory
import tkinter as tk 
import tkinter.filedialog as filedialog
import Backtesting.DelegationNetwork.DelegationTransferStrings as DTS

class WorkManager:
    STRATEGY_CHONK_SIZE = 500

    def __init__(self):
        root = tk.Tk()
        self.filenames = list(filedialog.askopenfilenames(parent=root, title='Choose a file'))
        root.withdraw() # make window go away 
        
        tickers = []
        print("Determining tickers...")
        for filename in self.filenames:
            ticker = getTickerFromFilename(filename)

            if ticker not in tickers:
                tickers.append(ticker)

        # update history
        print("updating history...")
        updateHistory(tickers) 
        print("\n========================================\n")

        self.strategiesChonksQueue = []
        self.currentWorkingFilename = None 

    def getWorkJson(self, cursor):
        while len(self.strategiesChonksQueue) == 0:
            # time to get more work
            if len(self.filenames) == 0:
                # no more files left - out of work 
                return None
            fullFilename = self.filenames.pop()
            self.currentWorkingFilename, ticker, datestr = getInfoFromFullFilename(fullFilename)
            self.strategiesChonksQueue = splitListIntoChonks(getStrategiesNotProcessed(ticker, datestr, cursor), WorkManager.STRATEGY_CHONK_SIZE)

        return json.dumps({
            DTS.STRATEGIES_KEY: self.strategiesChonksQueue.pop(),
            DTS.FILENAME_KEY: self.currentWorkingFilename
        })


    


        


