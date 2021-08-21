from mysql.connector import connect
from Backtesting.BacktestConfigMediator import getAllOptionsToTest, getStrategyInfoToTest
import CredentialsConfig.server_auth_config as db_auth_config

def insertStrategyIntoDB(name, aggregation, param1, param2, optionsString, cursor):
    cursor.execute("""
        INSERT INTO trading.strategy (name, aggregation, param1, param2, options_str)
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS(
            SELECT id \
            FROM trading.strategy as strat \
            WHERE \
                strat.name = %s \
                AND strat.aggregation = %s \
                AND strat.param1 = %s \
                AND strat.param2 = %s \
                AND strat.options_str = %s)""",
        (name, \
        str(aggregation),
        "None" if param1 == None else param1,
        "None" if param2 == None else param2,
        optionsString,
        name, \
        str(aggregation),
        "None" if param1 == None else param1,
        "None" if param2 == None else param2,
        optionsString))


# update strategy table by adding any permutations 
#   that do not exist in the table yet. 
# (standalone function to be called on its own)
def updateStrategyTable():
    with connect(
        host=db_auth_config.host,
        user=db_auth_config.userDB,
        password=db_auth_config.passwordDB,
        database=db_auth_config.database
    ) as connection, connection.cursor() as cursor:
        strategies = getStrategyInfoToTest()  
        optionsStrings = getAllOptionsToTest()

        for stratInfo in strategies:
            for optionsString in optionsStrings:
                    insertStrategyIntoDB(
                        stratInfo[0],
                        stratInfo[1],
                        stratInfo[2],
                        stratInfo[3],
                        optionsString,
                        cursor)

            connection.commit()


# get strategies that do not yet have a backtest entry for the given date and ticker
def getStrategiesNotProcessed(ticker, datestr, cursor):
    cursor.execute("""
        SELECT *
        FROM trading.strategy as strategy
        WHERE NOT EXISTS (
            SELECT null
            FROM trading.backtest as backtest
            WHERE strategy.id = backtest.strategy_id
                AND strategy.disabled = 0
                AND backtest.ticker = %s
                AND backtest.date = %s
        )""",
        (ticker, datestr))
    return cursor.fetchall()


def getStrategiesCount(cursor):
    cursor.execute("""SELECT count(*) FROM trading.strategy""")
    return cursor.fetchall()


def getDisabledStrategyIds(cursor):
    cursor.execute("""SELECT id FROM trading.strategy WHERE disabled = 1""")
    return cursor.fetchall()
