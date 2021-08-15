import config
import Network.TDAmeritrade as TDAmeritrade 
import DataManagement.DataTransferStrings as DataTransferStrings
import DataManagement.Auth.auth as auth
from mysql.connector import connect, Error 
import CredentialsConfig.db_auth_config as db_auth_config
import datetime 
import csv 



def updateHistory(tickers):
    auth.runUpdateToken()
    with connect(
            host=db_auth_config.host,
            user=db_auth_config.user,
            password=db_auth_config.password,
            database=db_auth_config.database
        ) as connection:
        with connection.cursor() as cursor:
            

            oldConfigValue = config.days_of_history_to_get
            config.days_of_history_to_get = 10
            for ticker in tickers:
                # Get latest timestamp saved in db
                cursor.execute("\
                    SELECT timestamp \
                    FROM trading.history \
                    WHERE \
                        ticker = %s\
                    ORDER BY timestamp desc \
                    LIMIT 1" % \
                    ("\"" + ticker + "\""))

                selectResult = cursor.fetchone()
                lastTimestampSaved = 0 if selectResult == None else selectResult[0]

                data_dict = TDAmeritrade.getPriceHistoryJson(ticker)
                # print(data_dict)
                for candle in data_dict[DataTransferStrings.CANDLES_KEY]:
                    candleTimestamp = candle[DataTransferStrings.CANDLE_TIMESTAMP_KEY]
                    if candleTimestamp > lastTimestampSaved:
                        cursor.execute("""
                            INSERT INTO trading.history (timestamp, ticker, open, close, high, low, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (candleTimestamp, \
                            ticker, \
                            candle[DataTransferStrings.CANDLE_OPEN_KEY], \
                            candle[DataTransferStrings.CANDLE_CLOSE_KEY], \
                            candle[DataTransferStrings.CANDLE_HIGH_KEY], \
                            candle[DataTransferStrings.CANDLE_LOW_KEY], \
                            candle[DataTransferStrings.CANDLE_VOLUME_KEY]))
                        connection.commit()
                print("finished for ticker " + ticker)

            config.days_of_history_to_get = oldConfigValue 



def getFirstTimestamp(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(reader)
        return row['Timestamp'] # first timestamp of tick data

def getHistory(filename, cursor, ticker):
    historyStopTimetamp = getFirstTimestamp(filename)
    historyStopDatetime = datetime.datetime.fromtimestamp(float(historyStopTimetamp)/1000.0)
    daysToSubtract = 2
    if historyStopDatetime.weekday() == 0:
        daysToSubtract += 2
    elif historyStopDatetime.weekday() == 6:
        daysToSubtract += 1
    startHistoryAtDatetime = historyStopDatetime - datetime.timedelta(days=daysToSubtract)
    startHistoryTimestamp = int(startHistoryAtDatetime.timestamp()*1000.0)

    # print("start: ", str(startHistoryTimestamp), " , stop: ", historyStopTimetamp)
    cursor.execute("\
        SELECT open, low, high, close \
        FROM trading.history \
        WHERE \
            ticker = %s \
            AND timestamp < %s \
            AND timestamp > %s" % \
        ("\"" + ticker + "\"", \
        str(historyStopTimetamp), \
        str(startHistoryTimestamp)))
    return cursor.fetchall()



# def main():
#     tickersString = input("tickers to update history: ")
#     updateHistory(tickersString.split())


# if __name__ == "__main__":
#     main()