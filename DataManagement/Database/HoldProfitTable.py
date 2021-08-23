from Tools.StringTools import getInfoFromFullFilename
from mysql.connector import connect
import CredentialsConfig.server_auth_config as db_auth_config
import csv 
import datetime 
import config 
import Tools.TimeManagement as TimeManagement

def rowExists(cursor, datestr, ticker):
    cursor.execute("""
        SELECT * 
        FROM trading.hold_profit
        WHERE ticker = %s
            AND date = %s""",
        (ticker, datestr))
    return len(cursor.fetchall())

def updateHoldProfitTable(filenames):
    with connect(
        host=db_auth_config.host,
        user=db_auth_config.userDB,
        password=db_auth_config.passwordDB,
        database=db_auth_config.database
    ) as connection, connection.cursor() as cursor:
        config.simulating = True 
        query = "INSERT IGNORE INTO trading.hold_profit (ticker, date, profit) VALUES "
        totalFileCountStr = str(len(filenames))
        count = 0
        for filename in filenames:
            count += 1
            print("processing file", str(count) + "/" + totalFileCountStr)
            _, ticker, datestr = getInfoFromFullFilename(filename)
            if not rowExists(cursor, datestr, ticker):
                # needs to be calculated and inserted
                startPrice = None  
                endPrice = None
                buy_start = config.getBuyStart(ticker)
                buy_stop = config.getBuyStop(ticker)
                lastLast = None 
                with open(filename, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader: 
                        dt = datetime.datetime.fromtimestamp(float(row['Timestamp'])/1000.0)
                        config.simulatingTimeStamp = dt
                        if row['Last'] != None and row['Last'] != "":
                            lastLast = float(row['Last'])

                        isInTimeSpan = TimeManagement.withinBuyingTimeConstraint(buy_start, buy_stop)
                        if startPrice == None and isInTimeSpan:
                            startPrice = lastLast
                        if not isInTimeSpan and endPrice == None and startPrice != None:
                            endPrice = lastLast 

                    if endPrice == None:
                        endPrice = lastLast 

                if startPrice == None or endPrice == None:
                    print("error: startPrice:", str(startPrice), "endPrice:", str(endPrice))
                else:
                    query += " (\"" + ticker + "\",\"" + datestr + "\"),"

        # remove trailing comma 
        query = query[:-1]
        cursor.execute(query)
        connection.commit()