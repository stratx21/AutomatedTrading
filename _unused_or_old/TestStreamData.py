from time import sleep
import Strategies.StrategyCreator as StrategyCreator
import Terminal.TerminalStrings as TerminalStrings
import csv 
from datetime import datetime 
import config 


def getStrategyPrintFormat(ticker, strat, aggregation, optionalArgument1 = None, optionalArgument2 = None):
    return ("["+ticker.upper()+"]: ("+aggregation+","+strat + ((","+str(optionalArgument1)) if optionalArgument1 != None else "") + ((","+str(optionalArgument2)) if (optionalArgument2 != None) else (""))+")")


# TODO script to see strategy, script to see file 



if __name__ == '__main__':
    terminate = False 
    started = False
    dataFileLocation = None 
    strategy = None 
    strategyParams = None 
    ticker = None 
    while not terminate:
        instr = input("TDA Automation> ")
        inputs = instr.split()
        
        if len(inputs) == 0:
            pass 
        elif inputs[0] == TerminalStrings.START:
            if started: 
                print(TerminalStrings.SYS_MESSAGE + " already started. start rejected")
            elif ticker == None:
                print("error - ticker is none")
            else: 
                strategy = StrategyCreator.create(*strategyParams)
                strategy.enablePostHistory()
                strategy.disable()
                config.simulating = True 

                with open(dataFileLocation, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    first = True 
                    lastTime = None 
                    lastBid = None 
                    lastAsk = None
                    for row in reader:
                        tmstmp = float(row['Timestamp'])/1000.0
                        timestampDatetime = datetime.fromtimestamp(tmstmp)
                        lastTime = timestampDatetime
                        config.simulatingTimeStamp = timestampDatetime
                        # TODO : remove this if 
                        if (config.buy_start.hour < timestampDatetime.hour or \
                            (config.buy_start.hour == timestampDatetime.hour and config.buy_start.minute <= timestampDatetime.minute)) \
                            and (timestampDatetime.hour < config.buy_stop.hour or (timestampDatetime.hour == config.buy_stop.hour and  timestampDatetime.minute <= config.buy_stop.minute)):
                            if first:
                                first = False 
                                print(TerminalStrings.WARNING + "allowing trading now at time: ", timestampDatetime)
                        else:
                            if not first:
                                first = True 
                                print(TerminalStrings.WARNING + "reached the end of the allowed time period.")
                                print("profit so far on day: " + str(strategy.profitSoFar))

                        if 'Bid' in row.keys()  and len(row['Bid']) > 0:
                            lastBid = float(row['Bid'])
                            strategy.setLastBid(lastBid)
                        if 'Ask' in row.keys()  and len(row['Ask']) > 0:
                            lastAsk = float(row['Ask'])
                            strategy.setLastAsk(lastAsk)

                        if ticker not in config.TICKERS_TO_AVG_BA and ticker not in config.TICKERS_TO_USE_ASK:
                            if 'Last' in row.keys() and len(row['Last']) > 0:
                                strategy.addPrice(float(row['Last']))
                        elif ticker in config.TICKERS_TO_USE_ASK:
                            # use the ask 
                            if lastAsk != None:
                                strategy.addPrice(lastAsk)
                        else: # ticker is in avg BA list 

                            if lastBid != None and lastAsk != None:
                                strategy.addPrice((lastAsk + lastBid)/2.0)

                
        elif inputs[0] == TerminalStrings.EXIT or inputs[0] == TerminalStrings.STOP:
            print(TerminalStrings.SYS_MESSAGE + " stopping...")
            if started:
                started = False
                sleep(2)
            else:
                print(TerminalStrings.SYS_MESSAGE + " nothing to stop")

            # only terminate program if input was exit not stop:
            terminate = inputs[0] == TerminalStrings.EXIT 

        elif inputs[0] == TerminalStrings.TICKER:
            if len(inputs) < 2:
                print("error: syntax: ticker \"ticker\"")
            else:
                ticker = inputs[1].upper()
                if strategyParams != None:
                    strategyParams[1] = ticker 

        elif inputs[0] == TerminalStrings.SET:
            if len(inputs) < 2:
                print("set [\"strategy\" aggregation stratName params] | [\"file\" dataFileLocation]")
            elif inputs[1] == "strategy":
                stratName = inputs[3].upper()
                aggregation = int(inputs[2])
                if not StrategyCreator.isStrategyName(stratName):
                    print(TerminalStrings.ERROR + " strategy \""+stratName+"\" not found! ")
                else:
                    if len(inputs) < 5:
                        strategyParams = [stratName, "fakeTicker" if ticker == None else ticker, aggregation]
                    elif len(inputs) < 6: 
                        strategyParams = [stratName, "fakeTicker" if ticker == None else ticker, aggregation, inputs[4]]
                    else: 
                        strategyParams = [stratName, "fakeTicker" if ticker == None else ticker, aggregation, inputs[4], inputs[5]]

            elif inputs[1] == "file":
                dataFileLocation = inputs[2]
        
        elif inputs[0] == TerminalStrings.STATUS:
            print("started:", str(started))
            print("params: " + str(*strategyParams))

        elif inputs[0] == TerminalStrings.STRATS:
            print("Strategies: ")
            for strat in StrategyCreator.acceptableStrategyNames:
                print("  - " + strat)
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
