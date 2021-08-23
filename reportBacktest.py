from Backtesting.ExcelGenerator import ExcelGenerator
from mysql.connector import connect, Error 
import CredentialsConfig.server_auth_config as db_auth_config

def getAllTickersFromDb():
    with connect(
        host=db_auth_config.host,
        user=db_auth_config.userDB,
        password=db_auth_config.passwordDB,
        database=db_auth_config.database
    ) as connection, connection.cursor() as cursor:
        cursor.execute("\
            SELECT DISTINCT ticker \
            FROM trading.backtest")

        return cursor.fetchall()
    return []

if __name__ == '__main__':
    for ticker in getAllTickersFromDb():
        gen = ExcelGenerator(ticker[0])
        gen.run()
