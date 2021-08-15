from Backtesting.ExcelGenerator import ExcelGenerator
from mysql.connector import connect, Error 

def getAllTickersFromDb():
    with connect(
        host="localhost",
        user="root",
        password="94358857",
        database="trading"
    ) as connection, connection.cursor() as cursor:
        cursor.execute("\
            SELECT DISTINCT ticker \
            FROM trading.backtesting_results")

        return cursor.fetchall()
    return []

if __name__ == '__main__':
    for ticker in getAllTickersFromDb():
        gen = ExcelGenerator(ticker[0])
        gen.run()
