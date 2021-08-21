from Backtesting.ExcelGenerator import ExcelGenerator
from mysql.connector import connect, Error 
import CredentialsConfig.db_auth_config as db_auth_config

def getAllTickersFromDb():
    with connect(
        host=db_auth_config.host,
        user=db_auth_config.user,
        password=db_auth_config.password,
        database=db_auth_config.database
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
