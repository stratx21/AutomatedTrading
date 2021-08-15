from multiprocessing import Pipe, Process 
import Network.TDAmeritrade as TDAmeritrade
import asyncio, nest_asyncio 
from DataManagement.DataSaveMediator import DataSaveMediator
import Terminal.TerminalStrings as TerminalStrings
import DataManagement.Auth.auth as auth
from time import sleep 
import json 
import DataManagement.DataTransferStrings as DataTransferStrings

nest_asyncio.apply() # TODO remove ? 


##############################################################################
# Process Run Functions: 

def runTDA(TDA_Send, tickersString):
    print(TerminalStrings.SYS_MESSAGE + " starting TDA service...") 
    tda = TDAmeritrade.TDAMeritrade(TDA_Send)
    
    loop = asyncio.get_event_loop()
    
    # Start connection and get client connection protocol
    connection = loop.run_until_complete(tda.startStreaming(tickersString, isJH2=True))


def runMediator(logic_Receive):
    print(TerminalStrings.SYS_MESSAGE + " starting Mediator service...")

    dataMediator = DataSaveMediator(logic_Receive)
    dataMediator.update()



if __name__ == '__main__':
    
    logic_Receive, TDA_Send = Pipe()
    
    
    TDA_Process = None 
    mediator_Process = None 
    
    tickersToTrack = []
     
    terminate = False 
    started = False 
    while not terminate: 
        instr = input("Save Data Stream> ")
        inputs = instr.split()
        
        if len(inputs) == 0:
            pass 
        elif inputs[0] == TerminalStrings.EXIT or inputs[0] == TerminalStrings.STOP:
            print(TerminalStrings.SYS_MESSAGE + " stopping...")
            if started:
                auth.tokenUpdateProcess.terminate()
                TDA_Send.send(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.TERMINATE}))
                TDA_Process.terminate()
                mediator_Process.terminate()
                started = False

            # only terminate program if input was exit not stop:
            terminate = inputs[0] == TerminalStrings.EXIT 
        elif inputs[0] == TerminalStrings.ADD:
            if len(inputs) < 2:
                print(TerminalStrings.WARNING + "too few arguments : add [ticker]")
            else:
                tickersToTrack.append(inputs[1])
            
        elif inputs[0] == TerminalStrings.START:
            if started: 
                print(TerminalStrings.SYS_MESSAGE + " already started. start rejected")
            else: 
                auth.init(True) # get auth and update if needed 
                mediator_Process = Process(target = runMediator, args = (logic_Receive,))
                mediator_Process.start()
                
                tickersString = ""
                for tickr in tickersToTrack:
                    tickersString += tickr+","
                tickersString = tickersString[:-1]
                TDA_Process = Process(target=runTDA, args=(TDA_Send, tickersString))
                
                TDA_Process.start()
                started = True 
                sleep(3)
                
                
        elif inputs[0] == TerminalStrings.STATUS:
            print("tickers: ")
            for ticker in tickersToTrack:
                print("\""+ticker+"\"")
                
                
        elif inputs[0] == TerminalStrings.REFRESH_TOKEN:
            if len(inputs) != 2 or not (inputs[1] == "expires" or inputs[1] == "get"):
                print(TerminalStrings.WARNING + " improper number of arguments passed. Please use this syntax: ")
                print(TerminalStrings.REFRESH_TOKEN + " [expires | get]")
            elif inputs[1] == "expires":
                print(auth.getRefreshTokenExpireTime(True))
            else: # is get 
                auth.updateRefreshToken(True)
        
                
            
                
        
    
    
    
    