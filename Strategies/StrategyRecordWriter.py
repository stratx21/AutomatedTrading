import os 
import csv 
import datetime 
import config 

fieldsStrategy = ['Simulated', 'Buy/Sell', 'Price']

def createFileStrategy(ticker, strategyname, aggregation):
    fileName = config.get_trade_records_directory() + str(datetime.datetime.now()).replace(":","_").replace(" ","_") +"___" +ticker+"_"+strategyname+"_"+aggregation+".csv"
    with open(fileName, 'w', newline='') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(fieldsStrategy)
    return fileName 

def addEntryStrategy(fileName, simulated, buysellorderstr, price):
    with open(fileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["1" if simulated else "0", buysellorderstr, str(price)])

fieldsDataSave = ['Timestamp', 'Last', 'Bid', 'Ask', 'Volume']

def createFileDataSave(ticker):
    fileName = config.records_directory + str("stream_"+ticker + "__" + str(datetime.datetime.now()).replace(":","_").replace(" ","_") + ".csv")
    with open(fileName, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldsDataSave)
    return fileName
    
    
def addEntryDataSave(fileName, timestamp, lastPrice, bidPrice, askPrice, volume):
    with open(fileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        last = "" if lastPrice == None else lastPrice
        bid  = "" if bidPrice  == None else bidPrice
        ask  = "" if askPrice  == None else askPrice
        vol  = "" if volume    == None else volume 
        writer.writerow([str(timestamp), last, bid, ask, vol]) # should already be str
         
