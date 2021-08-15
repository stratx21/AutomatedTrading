from time import sleep
import tkinter as tk 
from multiprocessing import Event 
# import finplot
# import pandas as pd 
import os 
from Terminal import TerminalStrings
from DataManagement import DataTransferStrings
import config
from multiprocessing import Process, Pipe
import json 


#TODO remove ? 
#ms delay if pipe has no data to check again in ms 
DELAY_PIPE_CHECKING = 100

# TODO organize into UI strings file ? 
OPEN_LABEL  = "open: "
CLOSE_LABEL = "close: "
LOW_LABEL   = "low: "
HIGH_LABEL  = "high: "

BUY_LABEL = "BUY"
SELL_LABEL= "SELL"

def getPriceOutputFormat(price):
        return "{:.2f}".format(price)

# shoshoni : bg : #372c22 , fg: #4af5e4


class ProcessLogWindowManager:

    def __init__(self, ticker, title):

        ui_receive, self.send_pipe = Pipe()
        
        self.windowProcess = Process(target = self.create, args = (ticker, title, ui_receive))
        self.windowProcess.start()
    
    def terminate(self):
        print("terminating UI window... ")
        self.send_pipe(json.dumps({DataTransferStrings.SERVICE_KEY: DataTransferStrings.TERMINATE}))
        self.windowProcess.terminate()

    def create(self, ticker, title, ui_receive_pipe):
        root = tk.Tk()
        instance = ProcessLogWindow(root, title, ui_receive_pipe, ticker)
        instance.pack()
        instance.updateLoop()


    def writeCandle(self, candle):
        self.send_pipe.send(json.dumps({
            DataTransferStrings.SERVICE_KEY: DataTransferStrings.LOG_WINDOW_CANDLE_KEY,
            DataTransferStrings.LOG_WINDOW_DATA_KEY: {
                DataTransferStrings.CANDLE_OPEN_KEY:  candle.open,
                DataTransferStrings.CANDLE_CLOSE_KEY: candle.close,
                DataTransferStrings.CANDLE_LOW_KEY:   candle.low,
                DataTransferStrings.CANDLE_HIGH_KEY:  candle.high
            }
        }))

    
    def writeBuyNotification(self, boughtPrice, quantity, isSimulated = False):
        self.send_pipe.send(json.dumps({
            DataTransferStrings.SERVICE_KEY: DataTransferStrings.LOG_WINDOW_BUY_KEY,
            DataTransferStrings.LOG_WINDOW_DATA_KEY: {
                DataTransferStrings.LOG_WINDOW_PRICE_KEY:         boughtPrice,
                DataTransferStrings.LOG_WINDOW_QUANTITY_KEY:      quantity,
                DataTransferStrings.LOG_WINDOW_IS_SIMULATED_KEY:  1 if isSimulated else 0
            }
        }))

    def writeSellNotification(self, soldPrice, profit, quantity, isSimulated = False):
        self.send_pipe.send(json.dumps({
            DataTransferStrings.SERVICE_KEY: DataTransferStrings.LOG_WINDOW_SELL_KEY,
            DataTransferStrings.LOG_WINDOW_DATA_KEY: {
                DataTransferStrings.LOG_WINDOW_PRICE_KEY:         soldPrice,
                DataTransferStrings.LOG_WINDOW_PROFIT_KEY:        profit,
                DataTransferStrings.LOG_WINDOW_QUANTITY_KEY:      quantity,
                DataTransferStrings.LOG_WINDOW_IS_SIMULATED_KEY:  1 if isSimulated else 0
            }
        }))

    def writePLSummary(self, profit, trades):
        self.send_pipe.send(json.dumps({
            DataTransferStrings.SERVICE_KEY: DataTransferStrings.LOG_WINDOW_PL_KEY,
            DataTransferStrings.LOG_WINDOW_DATA_KEY: {
                DataTransferStrings.LOG_WINDOW_PROFIT_KEY: profit,
                DataTransferStrings.LOG_WINDOW_TRADES_KEY: trades
            }
        }))

    def writeHistoryFinished(self, timeStartStr, timeEndStr):
        self.send_pipe.send(json.dumps({
            DataTransferStrings.SERVICE_KEY: DataTransferStrings.LOG_WINDOW_HISTORY_FIN_KEY,
            DataTransferStrings.LOG_WINDOW_DATA_KEY: {
                DataTransferStrings.TIME_START_KEY: timeStartStr,
                DataTransferStrings.TIME_STOP_KEY:  timeEndStr
            }
        }))


class ProcessLogWindow(tk.Frame):
    dataPipeIn = None 
    tkParent = None 
    line = 1
    ticker = None 
    isRunning = True 

    # TODO - disable close ? force close from terminal ? 

    def __init__(self, root, title, dataPipeIn, ticker = "NONE", bg="#1e1e1e", textDefaultColor = "#cccccc"):
        parent = root
        parent.title(title)
        parent.geometry("650x800")
        parent.configure(background=bg)
        parent.protocol("WM_DELETE_WINDOW", self.on_quit)
        
        tk.Frame.__init__(self, parent)

        self.tkParent = parent 
        self.dataPipeIn = dataPipeIn
        self.ticker = ticker 

        
        
        self.stop_event = Event() # TODO remove ? 
        self.text = tk.Text(parent)

        self.text["bg"] = bg
        self.text["fg"] = textDefaultColor

        # TODO - remove - testing 
        # self.text.insert(tk.END, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA sdknf jdsnfg jnsadfk nsdafnkjsdanjk nsjknsdjkanjsdank fkadjs")
        # self.text.insert(tk.END, "testtttt")

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand = tk.YES)
        self.text.config(state=tk.DISABLED)

        self.text.tag_configure("RED",           foreground="#d74646")
        self.text.tag_configure("GREEN",         foreground="#23d18b")
        self.text.tag_configure("SYS_MESSAGE",   foreground="#f5f543")
        self.text.tag_configure("STRAT_MESSAGE", foreground="#29b8db")

        self.scrollBar = tk.Scrollbar(parent, command=self.text.yview)
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        # self.scrollBar.grid(row=0, column=1, sticky='nsew')
        # self.text['yscrollcommand'] = self.scrollBar.set

        #self.text.tag_add("RED", "1.1", "1.10") # TODO remove - testing 

        #self.update()


        # self.pack()
        # self.updateLoop()

    def on_quit(self):
        self.isRunning = False 

    def updateLoop(self):
        self.tkParent.update()
        #while pipe has data, read and interpret: 
        while self.isRunning:
            while self.dataPipeIn.poll():
                data_dict = json.loads(self.dataPipeIn.recv())

                if DataTransferStrings.SERVICE_KEY not in data_dict.keys():
                    print(TerminalStrings.ERROR + " ProcessLoggingWindow.updateLoop service key not included. data given: ", json.dumps(data_dict))
                    continue  
                
                serviceKey = data_dict[DataTransferStrings.SERVICE_KEY]
                functData = data_dict[DataTransferStrings.LOG_WINDOW_DATA_KEY]

                if serviceKey == DataTransferStrings.LOG_WINDOW_CANDLE_KEY:
                    self.writeCandle(functData)

                elif serviceKey == DataTransferStrings.LOG_WINDOW_BUY_KEY:
                    self.writeBuyNotification(functData[DataTransferStrings.LOG_WINDOW_PRICE_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_QUANTITY_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_IS_SIMULATED_KEY])

                elif serviceKey == DataTransferStrings.LOG_WINDOW_SELL_KEY:
                    self.writeSellNotification(functData[DataTransferStrings.LOG_WINDOW_PRICE_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_PROFIT_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_QUANTITY_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_IS_SIMULATED_KEY])

                elif serviceKey == DataTransferStrings.LOG_WINDOW_PL_KEY:
                    self.writePLSummary(functData[DataTransferStrings.LOG_WINDOW_PROFIT_KEY],
                        functData[DataTransferStrings.LOG_WINDOW_TRADES_KEY])
                
                elif serviceKey == DataTransferStrings.LOG_WINDOW_HISTORY_FIN_KEY:
                    self.writeHistoryFinished(functData[DataTransferStrings.TIME_START_KEY],
                        functData[DataTransferStrings.TIME_STOP_KEY])

                elif serviceKey == DataTransferStrings.TERMINATE:
                    self.on_quit()
                    self.quit()

            sleep(config.DELAY_PIPE_CHECKING/1000.0)
            # sleep(0.01)

            self.tkParent.update()
    
    def addText(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text)
        self.text.config(state=tk.DISABLED)

    def newLine(self):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writeLine(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, text)
        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writeCandle(self, candle):
        self.text.config(state=tk.NORMAL)
        #charPosition = 0
        currentLineStr = str(self.line)

        open = float(candle[DataTransferStrings.CANDLE_OPEN_KEY])
        close= float(candle[DataTransferStrings.CANDLE_CLOSE_KEY])

        openPriceStr  = OPEN_LABEL  + getPriceOutputFormat(open)  + " "
        closePriceStr = CLOSE_LABEL + getPriceOutputFormat(close) + " "
        lowPriceStr   = LOW_LABEL   + getPriceOutputFormat(candle[DataTransferStrings.CANDLE_LOW_KEY])   + " "
        highPriceStr  = HIGH_LABEL  + getPriceOutputFormat(candle[DataTransferStrings.CANDLE_HIGH_KEY])  + " "

        # ticker 
        self.text.insert(tk.END, self.ticker + " ")
        self.text.tag_add("GREEN" if close >= open else "RED", 
            currentLineStr+".0", 
            currentLineStr+"."+str(len(self.ticker)))
        #charPosition += len(self.ticker) + 1 # 1 for space 

        
        self.text.insert(tk.END, openPriceStr)
        self.text.insert(tk.END, closePriceStr)
        self.text.insert(tk.END, lowPriceStr)
        self.text.insert(tk.END, highPriceStr)

        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writeBuyNotification(self, boughtPrice, quantity, isSimulated = False):
        self.text.config(state=tk.NORMAL)
        charPosition = 0
        currentLineStr = str(self.line)

        # ticker 
        self.text.insert(tk.END, TerminalStrings.STRATEGY_NC + " ")
        charPosition += len(TerminalStrings.STRATEGY_NC) + 1 # 1 for space 
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+".0", 
            currentLineStr+"."+str(charPosition))
        
        self.text.insert(tk.END, self.ticker + " ")
        charPosition += len(self.ticker) + 1 # 1 for space 

        self.text.insert(tk.END, TerminalStrings.TRADE_NOTIFICATION_NC + " ") 
        strlen = len(TerminalStrings.TRADE_NOTIFICATION_NC) + 1 # 1 for space
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+"."+str(charPosition), 
            currentLineStr+"."+str(charPosition+strlen))
        charPosition += strlen

        if isSimulated:
            self.text.insert(tk.END, TerminalStrings.SIMULATED_NC + " ") 
            strlen = len(TerminalStrings.SIMULATED_NC) + 1 # 1 for space
            self.text.tag_add("SYS_MESSAGE", 
                currentLineStr+"."+str(charPosition), 
                currentLineStr+"."+str(charPosition+strlen))
            charPosition += strlen

        self.text.insert(tk.END, BUY_LABEL + " ") 
        strlen = len(BUY_LABEL) + 1 # 1 for space
        self.text.tag_add("GREEN", 
            currentLineStr+"."+str(charPosition), 
            currentLineStr+"."+str(charPosition+strlen))
        charPosition += strlen

        quantityStr = str(quantity)
        self.text.insert(tk.END, "+" + quantityStr + " ") 

        quantityStr = str(quantity)
        self.text.insert(tk.END, "at " + getPriceOutputFormat(boughtPrice) + " ") 

        # NOTE : character position not updated for last few parts at this point 

        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writeSellNotification(self, soldPrice, profit, quantity, isSimulated = False):
        self.text.config(state=tk.NORMAL)
        charPosition = 0
        currentLineStr = str(self.line)

        # ticker 
        self.text.insert(tk.END, TerminalStrings.STRATEGY_NC + " ")
        charPosition += len(TerminalStrings.STRATEGY_NC) + 1 # 1 for space 
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+".0", 
            currentLineStr+"."+str(charPosition))
        
        self.text.insert(tk.END, self.ticker + " ")
        charPosition += len(self.ticker) + 1 # 1 for space 

        self.text.insert(tk.END, TerminalStrings.TRADE_NOTIFICATION_NC + " ") 
        strlen = len(TerminalStrings.TRADE_NOTIFICATION_NC) + 1 # 1 for space
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+"."+str(charPosition), 
            currentLineStr+"."+str(charPosition+strlen))
        charPosition += strlen

        if isSimulated:
            self.text.insert(tk.END, TerminalStrings.SIMULATED_NC + " ") 
            strlen = len(TerminalStrings.SIMULATED_NC) + 1 # 1 for space
            self.text.tag_add("SYS_MESSAGE", 
                currentLineStr+"."+str(charPosition), 
                currentLineStr+"."+str(charPosition+strlen))
            charPosition += strlen

        self.text.insert(tk.END, SELL_LABEL + " ") 
        strlen = len(BUY_LABEL) + 1 # 1 for space
        self.text.tag_add("RED", 
            currentLineStr+"."+str(charPosition), 
            currentLineStr+"."+str(charPosition+strlen))
        charPosition += strlen

        quantityStr = str(quantity)
        self.text.insert(tk.END, "-" + quantityStr + " ") 
        charPosition += len(quantityStr) + 2

        soldStr = "at " + getPriceOutputFormat(soldPrice)
        self.text.insert(tk.END, soldStr) 
        charPosition += len(soldStr)

        charPosition += 1 # why? I'm not sure. but it's what it needs. 
        profitStr = "; diff: " + getPriceOutputFormat(profit)
        self.text.insert(tk.END, profitStr)
        self.text.tag_add("RED" if profit < 0 else "GREEN", 
            currentLineStr+"."+str(charPosition+1), 
            currentLineStr+"."+str(charPosition+len(profitStr)))

        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writePLSummary(self, profit, trades):
        self.text.config(state=tk.NORMAL)
        charPosition = 0
        currentLineStr = str(self.line)

        # ticker 
        self.text.insert(tk.END, TerminalStrings.STRATEGY_NC + " ")
        charPosition += len(TerminalStrings.STRATEGY_NC) + 1 # 1 for space 
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+".0", 
            currentLineStr+"."+str(charPosition))
        
        profitStr = "profit so far: " + getPriceOutputFormat(profit) + " "
        self.text.insert(tk.END, profitStr)
        self.text.tag_add("RED" if profit < 0 else "GREEN", 
            currentLineStr+"."+str(charPosition), 
            currentLineStr+"."+str(charPosition+len(profitStr)))

        tradesStr = " over " + str(trades) + " trades"
        self.text.insert(tk.END, tradesStr) 

        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

    def writeHistoryFinished(self, startTimeStr, stopTimeStr):
        self.text.config(state=tk.NORMAL)
        charPosition = 0
        currentLineStr = str(self.line)

        # ticker 
        self.text.insert(tk.END, TerminalStrings.STRATEGY_NC + " ")
        charPosition += len(TerminalStrings.STRATEGY_NC) + 1 # 1 for space 
        self.text.tag_add("STRAT_MESSAGE", 
            currentLineStr+".0", 
            currentLineStr+"."+str(charPosition))
        
        self.text.insert(tk.END, 
            "history finished. trading from " + startTimeStr + " - " + stopTimeStr)

        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        self.line += 1
        self.text.yview("scroll", 1, "units")

# if os.environ.get('DISPLAY','') == '':
#     print('no display found. Using :0.0')
#     os.environ.__setitem__('DISPLAY', ':0.0')

# startProcessLogWindow(None, "TITLEEEEEEEE")

# if __name__ == '__main__':
#     manager = ProcessLogWindowManager("faketicker", "title!")

#     while True:
#         print("out!")
#         sleep(5)








#df = pd.DataFrame({'Open': [35, 25], 'Close': [50,45], 'High': [51,46], 'Low': [30, 20]}) #(35,50,51,30)#, (25, 45, 46, 20)


# ax, ax2 = finplot.create_plot("TICKER", rows=2)

# finplot.candlestick_ochl(df[['Open', 'Close', 'High', 'Low']], ax=ax)
# finplot.autoviewrestore()
# finplot.show()