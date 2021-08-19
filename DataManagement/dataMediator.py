from os import error
import Terminal.TerminalStrings as TerminalStrings 
from time import sleep 
import json 
import config 
import Tools.TimeManagement as TimeManagement
import DataManagement.DataTransferStrings as DataTransferStrings
from DataManagement.DataSaveMediator import DataSaveMediator
from multiprocessing import Pipe, Process

class DataMediator:

    def __init__(self, strategyManager, dataPipeIn, tickersToStream = None):
        self.dataPipeIn = dataPipeIn
        self.strategyManager = strategyManager
        self.streaming = False 
        self.tickersToStream = None 
        self.pipeToStreamMediator = None 
        self.streamMediatorProcess = None 
        if tickersToStream != None and len(tickersToStream) > 0:
            self.tickersToStream = tickersToStream
            self.streaming = True 
            pipeFromMediator, self.pipeToStreamMediator = Pipe()
            self.streamMediatorProcess = Process(target = self.startStreamMediator, args = (tickersToStream, pipeFromMediator))
            self.streamMediatorProcess.start()

    def update(self):
        baDatas = {} # ticker : B, A
        #while pipe has data (sent from TDA), read and send to StrategyManager: 
        while True: 
            #while has data: 
            while self.dataPipeIn.poll():
                #handle data: 

                fromPipe = self.dataPipeIn.recv() # fromPipe = data from pipe 
                data_dict = json.loads(fromPipe)

                # TERMINATE
                if data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.TERMINATE:
                    self.strategyManager.terminateAll()
                    self.streamMediatorProcess.terminate()
                    break 

                
                # TODO combine below custom messages into one elif statement 
                #   - use or's, get ticker, pass in DataTransferStrings.SERVICE_KEY

                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.GUI:
                    ticker = data_dict[DataTransferStrings.TICKER_KEY]
                    self.strategyManager.sendMessageToTicker(ticker, DataTransferStrings.GUI)

                # ENABLE-POST-HISTORY : enable buying and printing trades after history entered
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.SENDING_HISTORY_ENABLE:
                    ticker = data_dict[DataTransferStrings.TICKER_KEY]
                    self.strategyManager.sendMessageToTicker(ticker, DataTransferStrings.SENDING_HISTORY_ENABLE)


                # DISABLE
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.DISABLE:
                    ticker = data_dict[DataTransferStrings.TICKER_KEY]
                    self.strategyManager.sendMessageToTicker(ticker, DataTransferStrings.DISABLE)

                # ENABLE
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.ENABLE:
                    ticker = data_dict[DataTransferStrings.TICKER_KEY]
                    self.strategyManager.sendMessageToTicker(ticker, DataTransferStrings.ENABLE)

                # OPT
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.OPT:
                    ticker = data_dict[DataTransferStrings.TICKER_KEY]
                    self.strategyManager.sendMessageToTicker(ticker, json.dumps(data_dict))




                # PRICE HISTORY
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.PRICE_HISTORY_KEY:
                    if DataTransferStrings.SYMBOL_KEY in data_dict:
                        ticker = data_dict[DataTransferStrings.SYMBOL_KEY]
                        for candle in data_dict[DataTransferStrings.CANDLES_KEY]:
                            for key in [DataTransferStrings.CANDLE_OPEN_KEY, DataTransferStrings.CANDLE_LOW_KEY, DataTransferStrings.CANDLE_HIGH_KEY, DataTransferStrings.CANDLE_CLOSE_KEY]:
                                if key in candle.keys():
                                    self.strategyManager.sendPrice(ticker, candle[key])
                                else:
                                    print(TerminalStrings.ERROR + " " + key + " not found for candle in price history, candle: " + json.dumps(candle))
                    else:
                        print(TerminalStrings.ERROR + " symbol not found in DataMediator price history receive")

                # QUOTE
                # if is a quote, get last price for each and send to StrategyManager
                elif data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.QUOTE_SERVICE_KEY:
                    for stockContent in data_dict[DataTransferStrings.CONTENT_KEY]:
                        if DataTransferStrings.KEY_KEY not in stockContent.keys():
                            print(TerminalStrings.ERROR + " key (key) (for ticker) not included in data (DataMediator.py) ")
                        else:
                            # get data needed: 
                            ticker = stockContent[DataTransferStrings.KEY_KEY]
                            newBid, newAsk = None, None 
                            if DataTransferStrings.BID_PRICE_KEY in stockContent.keys():
                                newBid = float(stockContent[DataTransferStrings.BID_PRICE_KEY])
                            if DataTransferStrings.ASK_PRICE_KEY in stockContent.keys():
                                newAsk = float(stockContent[DataTransferStrings.ASK_PRICE_KEY])

                            # TODO add volume 

                            if ticker not in baDatas.keys():
                                baDatas[ticker] = [-1.0, -1.0] # Bid, Ask
                            if newBid != None:
                                baDatas[ticker][0] = newBid
                            if newAsk != None:
                                baDatas[ticker][1] = newAsk

                            # check if BA should be used, and update latest BA data (kept for avg)
                            useBA = False 
                            if ticker in config.TICKERS_TO_AVG_BA and TimeManagement.marketIsOpen():
                                
                                # data added now

                                # use BA if neither B nor A are at the initial invalid value 
                                useBA = not ((baDatas[ticker][0] == -1.0) or (baDatas[ticker][1] == -1.0)) 
                                

                                if useBA:
                                    #then price to add is average of B/A
                                    self.strategyManager.sendPrice(ticker, round((baDatas[ticker][0] + baDatas[ticker][1])/2.0,2), newBid, newAsk)


                            # if
                            if (not useBA) and ticker in config.TICKERS_TO_USE_ASK and TimeManagement.marketIsOpen():
                                # use ask price to send to strategy 
                                if newAsk != None:
                                    self.strategyManager.sendPrice(ticker, newAsk, newBid, newAsk)


                            # BA nor Ask only not used for a price, and last price included in quote 
                            elif (not useBA) and DataTransferStrings.LAST_PRICE_KEY in stockContent.keys(): # () statement will only be false if the BA or Aonly WAS used  
                                #then send regular price if it was included:
                                #use last received bid and ask for update 
                                self.strategyManager.sendPrice(ticker, stockContent[DataTransferStrings.LAST_PRICE_KEY], baDatas[ticker][0], baDatas[ticker][1])

                else:
                    print("received unexpected data type in DataMediator \"" + data_dict[DataTransferStrings.SERVICE_KEY] + "\"")
                


                # Manage streaming: (bottom for low priority)
                if self.streaming:
                    self.pipeToStreamMediator.send(fromPipe)




            sleep(config.DELAY_PIPE_CHECKING/1000.0)


    def startStreamMediator(self, tickersToStream, pipeFromMediator):
        dataSaveMediator = DataSaveMediator(pipeFromMediator, tickersToStream=tickersToStream)
        dataSaveMediator.update()