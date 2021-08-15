from Terminal import TerminalStrings
from Strategies.Strategy import Strategy
import Strategies.StrategyCreator as StrategyCreator
from time import sleep 
from config import DELAY_PIPE_CHECKING
from multiprocessing import Process, Pipe
import DataManagement.DataTransferStrings as DataTransferStrings
import json 

#Strategy Process Manager takes a single strategy and 
# runs it with a process. 

#rather than the class being contained in a process like DataMediator
# is, StrategyProcessManager manages the process within itself. 

#strategies held within their own processes so their processing power allocation 
# is less interfered with. 

class StrategyProcessManager:

    def __init__(self, strategyName, strategyTicker, strategyAggregation, optionalArg1, optionalArg2):

        strategyReceive, self.sendToStrategyPipe = Pipe()

        self.process = Process(target = self.update, args = (strategyName, strategyTicker, strategyAggregation, strategyReceive, optionalArg1, optionalArg2))
        self.process.start()

    #WITHIN THE PROCESS: 
    def update(self, strategyName, strategyTicker, strategyAggregation, dataPipeIn, optionalArg1, optionalArg2):
        # map to requested strategy 
        strategy = StrategyCreator.create(strategyName, strategyTicker, strategyAggregation, optionalArg1, optionalArg2)

        #while pipe has data, read and send to onDataFunction: 
        while True:
            while dataPipeIn.poll():
                data = dataPipeIn.recv()
                if data == DataTransferStrings.DISABLE:
                    strategy.disable()
                elif data == DataTransferStrings.ENABLE:
                    strategy.enable()
                elif data == DataTransferStrings.SENDING_HISTORY_ENABLE:
                    strategy.enablePostHistory()
                elif data == DataTransferStrings.TERMINATE:
                    strategy.terminateUI()
                elif data == DataTransferStrings.GUI:
                    strategy.initUI()
                else: # is a dict 
                    data_dict = json.loads(data)

                    if DataTransferStrings.SERVICE_KEY in data_dict.keys():
                        # is custom message, but with data 
                        if data_dict[DataTransferStrings.SERVICE_KEY] == DataTransferStrings.OPT:
                            strategy.addOption(data_dict[DataTransferStrings.OPT_CHOICE_KEY], data_dict[DataTransferStrings.OPT_ARG_KEY])
                        else: 
                            print(TerminalStrings.ERROR + " StrategyProcessManager.update, dict, invalid service key \"" + data_dict[DataTransferStrings.SERVICE_KEY] + "\" given.")
                    else: 
                        # not a custom message - is quote data

                        last, bid, ask = data_dict['last'], data_dict['bid'], data_dict['ask'] # strings 

                        # needs new b/a to have more accurate buy/sell prediction
                        if bid != "None":
                            strategy.setLastBid(float(bid))
                        if ask != "None":
                            strategy.setLastAsk(float(ask))

                        strategy.addPrice(float(last)) # currently last will always exist 
                    
            sleep(DELAY_PIPE_CHECKING/1000.0)

    def terminateStrategyProcess(self):
        #  TODO / NOTE : terminate flow gets up to but not into here
        print('got here')
        self.sendCustomMessage(DataTransferStrings.TERMINATE)
        sleep(1)
        self.process.terminate()

    def sendPriceUpdate(self, newPriceJsonStr):
        self.sendToStrategyPipe.send(newPriceJsonStr)
        
    def sendCustomMessage(self, message):
        self.sendToStrategyPipe.send(message)