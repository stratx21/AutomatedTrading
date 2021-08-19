import os
import Strategies.StrategyCreator as StrategyCreator
import json
from Strategies.StrategyManager import StrategyManager
from DataManagement.dataMediator import DataMediator
# from Strategies.StrategyProcessManager import StrategyProcessManager
# from UI.ProcessLoggingWindow import ProcessLogWindow
import Network.TDAmeritrade as TDAMeritrade
import nest_asyncio
import asyncio
# from time import sleep 
from multiprocessing import Pipe, Process
import Terminal.TerminalStrings as TerminalStrings
import DataManagement.Auth.auth as auth
import DataManagement.DataTransferStrings as DataTransferStrings
from time import sleep 
import config 


nest_asyncio.apply() 


def removeDuplicatesFromList(list):
    toReturn = [] 
    for entry in list: 
        if entry not in toReturn:
            toReturn.append(entry)

##############################################################################
# Process Run Functions: 

def runTDA(TDA_Send, tickersString):
    print(TerminalStrings.SYS_MESSAGE + " starting TDA service...") 
    tda = TDAMeritrade.TDAMeritrade(TDA_Send)
    
    loop = asyncio.get_event_loop()
    
    # Start connection and get client connection protocol
    connection = loop.run_until_complete(tda.startStreaming(tickersString))


def runMediator(logic_Receive, strategies, tickersToStream = None):
    print(TerminalStrings.SYS_MESSAGE + " starting Mediator service...")

    strategyManager = StrategyManager()
    for key in strategies.keys():
        listd = strategies[key]
        if len(listd) > 3:
            strategyManager.addStrategy(listd[0], key, listd[1], listd[2], listd[3])
        elif len(listd) > 2:
            strategyManager.addStrategy(listd[0], key, listd[1], listd[2])
        else:
            strategyManager.addStrategy(listd[0], key, listd[1])


    dataMediator = DataMediator(strategyManager, logic_Receive, tickersToStream)
    dataMediator.update()





# no, there's not a ton of data validation. 


if __name__ == '__main__':

    logic_Receive, TDA_Send = Pipe()

    TDA_Process = None 
    mediator_Process = None 

    # [ticker]: (StrategyName, Aggregation, ?optionalArgument1)
    strategies = {}
    tickersToStream = []

    ##################################
    # User Input Terminal Section: 
    terminate = False 
    started = False
    while not terminate:
        instr = input("TDA Automation> ")
        inputs = instr.split()
        
        if len(inputs) == 0:
            continue 
        elif inputs[0] == TerminalStrings.EXIT or inputs[0] == TerminalStrings.STOP:
            print(TerminalStrings.SYS_MESSAGE + " stopping...")
            if started:
                auth.tokenUpdateProcess.terminate()
                TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.TERMINATE}))
                sleep(1)
                TDA_Process.terminate()
                mediator_Process.terminate()
                started = False
                sleep(2)
            else:
                print(TerminalStrings.SYS_MESSAGE + " nothing to stop")

            # only terminate program if input was exit not stop:
            terminate = inputs[0] == TerminalStrings.EXIT 

        elif inputs[0] == TerminalStrings.START:
            if started: 
                print(TerminalStrings.SYS_MESSAGE + " already started. start rejected")
            else: 
                auth.init() # get auth and update if neeeded 
                logic_Receive, TDA_Send = Pipe()
                mediator_Process = Process(target = runMediator, args = (logic_Receive, strategies, tickersToStream))
                mediator_Process.start()

                tickersString = ""
                # add tickers for strategies:
                for tickr in strategies.keys(): 
                    tickersString += tickr + ","

                # add tickers for streaming:
                for tickr in tickersToStream:
                    if tickr not in strategies.keys():
                        tickersString += tickr + ","

                tickersString = tickersString[:-1] # remove comma at the end 
                TDA_Process = Process(target = runTDA, args = (TDA_Send, tickersString))

                # add records/trades dir if it doesn't exist to prepare for records 
                if not os.path.exists(config.get_trade_records_directory()):
                    os.makedirs(config.get_trade_records_directory())

                # update with price history before TDA streaming starts: 
                for tickr in strategies.keys():
                    TDAMeritrade.addPriceHistory(tickr, TDA_Send)
                    # enable strategy for after history is done:
                    TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.SENDING_HISTORY_ENABLE, DataTransferStrings.TICKER_KEY: tickr}))


                TDA_Process.start()
                started = True 
                sleep(3) # let it all start before more input 

        elif inputs[0] == TerminalStrings.ADD:
            if len(inputs) < 4:
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print("add Ticker Aggregation StrategyName")
            else: 
                ticker = inputs[1].upper()
                stratName = inputs[3].upper()
                aggregation = inputs[2]
                if not StrategyCreator.isStrategyName(stratName):
                    print(TerminalStrings.ERROR + " strategy \""+stratName+"\" not found! ")
                else: 
                    if len(inputs) < 5:
                        strategies[ticker] = (stratName, aggregation, None, None)
                    elif len(inputs) < 6: 
                        strategies[ticker] = (stratName, aggregation, inputs[4], None)
                    else: 
                        strategies[ticker] = (stratName, aggregation, inputs[4], inputs[5])
                    print("added strategy "+TerminalStrings.getStrategyPrintFormat(ticker, stratName, aggregation, None if (len(inputs) < 5) else inputs[4]),None if (len(inputs) < 6) else inputs[5])
        
        elif inputs[0] == TerminalStrings.REMOVE or inputs[0] == TerminalStrings.REMOVE_SHORTHAND:
            if len(inputs) != 2:
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print("[remove | rm] Ticker")
            else:
                ticker = inputs[1].upper(),
                popped = strategies.pop(ticker)
                print("removed strategy: "+TerminalStrings.getStrategyPrintFormat(ticker, popped[0], popped[1]))
        
        elif inputs[0] == TerminalStrings.DISABLE:
            if len(inputs) != 2:
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print("disable Ticker")
            else:
                TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.DISABLE, DataTransferStrings.TICKER_KEY: inputs[1].upper()}))
        
        elif inputs[0] == TerminalStrings.ENABLE:
            if len(inputs) != 2:
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print("enable Ticker")
            else:
                TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.ENABLE, DataTransferStrings.TICKER_KEY: inputs[1].upper()}))
        
        elif inputs[0] == TerminalStrings.STATUS:
            print("started:", str(started))
            print("Strategies: ")
            for stratkey in strategies.keys():
                print("  " + TerminalStrings.getStrategyPrintFormat(stratkey, 
                                strategies[stratkey][0], 
                                strategies[stratkey][1],
                                strategies[stratkey][2],
                                strategies[stratkey][3]))

            print("tickers to stream: ")
            print(*tickersToStream, sep=", ")

        elif inputs[0] == TerminalStrings.REFRESH_TOKEN:
            if len(inputs) != 2 or not (inputs[1] == "expires" or inputs[1] == "get"):
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print(TerminalStrings.REFRESH_TOKEN + " [expires | get]")
            elif inputs[1] == "expires":
                print(auth.getRefreshTokenExpireTime())
            else: # is get 
                auth.updateRefreshToken()

        elif inputs[0] == TerminalStrings.STRATS:
            print("Strategies: ")
            for strat in StrategyCreator.acceptableStrategyNames:
                print("  - " + strat)

        elif inputs[0] == TerminalStrings.STREAM:
            if len(inputs) > 1:
                if inputs[1] == TerminalStrings.ADD:
                    if len(inputs) < 3:
                        print(TerminalStrings.WARNING + " too few arguments : stream add [ticker]+")
                    else: 
                        for entry in range(2, len(inputs)):
                            tickr = inputs[entry].upper()
                            if tickr not in tickersToStream:
                                tickersToStream.append(tickr)

                if inputs[1] == TerminalStrings.REMOVE or inputs[1] == TerminalStrings.REMOVE_SHORTHAND:
                    if len(inputs) != 3:
                        print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                        print("stream [remove | rm] Ticker")
                    else:
                        ticker = inputs[2].upper()
                        if ticker in tickersToStream:
                            tickersToStream.remove(ticker)
                            print(TerminalStrings.SYS_MESSAGE + " removed " + ticker + " from stream.")
                        else:
                            print(TerminalStrings.WARNING + " error: ticker \""+ticker+"\" not found in tickers to stream.")

        elif inputs[0] == TerminalStrings.OPT:
            if len(inputs) < 3:
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print("opt [ticker] [option] [args[]]")
            else:
                inputs.pop(0) # opt command 
                ticker = inputs.pop(0)
                optChoice = inputs.pop(0)
                # now inputs array is the array of arguments
                TDA_Send.send(json.dumps({
                    DataTransferStrings.SERVICE_KEY: DataTransferStrings.OPT, 
                    DataTransferStrings.TICKER_KEY: ticker.upper(),
                    DataTransferStrings.OPT_CHOICE_KEY: optChoice,
                    DataTransferStrings.OPT_ARG_KEY: inputs
                    }))

        elif inputs[0] == TerminalStrings.HELP:
            print(TerminalStrings.HELP_OUTPUT)

        elif inputs[0] == TerminalStrings.GUI:
            if len(inputs) < 2:
                print("syntax: gui ticker")
            else:
                TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.GUI, DataTransferStrings.TICKER_KEY: inputs[1].upper()}))

        else: 
            print("input \"" + instr + "\" is not recognized.")
    
    print(TerminalStrings.SYS_MESSAGE + " EXITED")

    ########################################
    #Pipe Notes: 
    # send, receive 
    # 
    # TDA_Receive = toTDAFromLogic
    # logic_Send = fromLogicToTDA
    # logic_Receive = toLogicFromTDA
    # TDA_Send = fromTDAToLogic
