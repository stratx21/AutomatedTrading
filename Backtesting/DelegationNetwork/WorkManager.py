import json
from Tools.ListTools import splitListIntoChonks
from DataManagement.Database.StrategyTable import getStrategiesNotProcessed
from Tools.StringTools import getInfoFromFullFilename
from DataManagement.Database.HistoryTable import updateHistory
from tkinter import Tk, filedialog
from CredentialsConfig.server_auth_config import streamRecordsDirectory
import Backtesting.DelegationNetwork.DelegationTransferStrings as DTS

class WorkManager:
    STRATEGY_CHONK_SIZE = 5000

    def __init__(self):
        root = Tk.Tk()
        self.filenames = filedialog.askopenfilenames(parent=root, title='Choose a file')
        root.withdraw() # make window go away 

        self.filesPerTicker = {}

        # update history
        print("updating history...")
        updateHistory(self.filesPerTicker.keys()) 
        print("\n========================================\n")

        self.strategiesChonksQueue = []
        self.currentWorkingFilename = None 

    def getWorkJson(self, cursor):
        while len(self.strategiesChonksQueue) == 0:
            # time to get more work
            fullFilename = self.filenames.pop()
            self.currentWorkingFilename, ticker, datestr = getInfoFromFullFilename(fullFilename)
            self.strategiesChonksQueue = splitListIntoChonks(getStrategiesNotProcessed(ticker, datestr, cursor))

        return json.dumps({
            DTS.STRATEGIES_KEY: self.strategiesChonksQueue.pop(),
            DTS.DTS.FILENAME_KEY: self.currentWorkingFilename
        })


    


        


