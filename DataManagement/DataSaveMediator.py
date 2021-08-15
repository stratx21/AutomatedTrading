
import DataManagement.DataTransferStrings as DataTransferStrings
import Terminal.TerminalStrings as TerminalStrings
import Strategies.StrategyRecordWriter as StrategyRecordWriter
import json 


class DataSaveMediator:
    
    def __init__(self, dataPipeIn, tickersToStream = None):
        self.dataPipeIn = dataPipeIn
        self.csvFiles = {}
        self.specifiedTickers = False 
        if tickersToStream != None:
            self.specifiedTickers = True 
            self.tickersToStream = tickersToStream

    def update(self):
        while True:
            data_dict = json.loads(self.dataPipeIn.recv())

            self.processDataDict(data_dict)
            
    def processDataDict(self, data_dict):
        # QUOTE DATA 
        if data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.QUOTE_SERVICE_KEY:
            timestamp = data_dict[DataTransferStrings.TIMESTAMP_KEY]
            for stockContent in data_dict[DataTransferStrings.CONTENT_KEY]:
                if DataTransferStrings.KEY_KEY not in stockContent.keys():
                    print(TerminalStrings.ERROR + " key (key) (for ticker) not included in data (DataMediator.py) ")
                else:
                    ticker = stockContent[DataTransferStrings.KEY_KEY]

                    if (not self.specifiedTickers) or ticker in self.tickersToStream:

                        #has last price - record last and timestamp
                        if ticker not in self.csvFiles.keys():
                            self.csvFiles[ticker] = StrategyRecordWriter.createFileDataSave(ticker)

                        # runs if first - key error does not occur 
                        last = stockContent[DataTransferStrings.LAST_PRICE_KEY] if DataTransferStrings.LAST_PRICE_KEY in stockContent.keys() else "" 
                        bid  = stockContent[DataTransferStrings.BID_PRICE_KEY] if DataTransferStrings.BID_PRICE_KEY in stockContent.keys() else "" 
                        ask  = stockContent[DataTransferStrings.ASK_PRICE_KEY] if DataTransferStrings.ASK_PRICE_KEY in stockContent.keys() else "" 
                        vol  = stockContent[DataTransferStrings.VOLUME_KEY] if DataTransferStrings.VOLUME_KEY in stockContent.keys() else "" 

                        StrategyRecordWriter.addEntryDataSave(self.csvFiles[ticker], timestamp, last, bid, ask, vol)
                        
                        
                             
                            
                    
            
    
    
    
    