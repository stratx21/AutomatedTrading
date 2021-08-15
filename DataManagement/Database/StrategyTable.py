from mysql.connector import connect, Error 
from Backtesting.BacktestConfigMediator import getAllOptionsToTest, getStrategyInfoToTest

# unused?
def strategyExistsInDB(name, aggregation, param1, param2, optionsString, cursor):
    cursor.execute("\
        SELECT id \
        FROM trading.strategy \
        WHERE \
            name = %s \
            AND aggregation = %s \
            AND param1 = %s \
            AND param2 = %s \
            AND options_str = %s" % \
            ("\"" + name + "\"", \
            str(aggregation),
            "\"" + ("None" if param1 == None else param1) + "\"",
            "\"" + ("None" if param2 == None else param2) + "\"",
            "\"" + optionsString + "\""))
    return len(cursor.fetchall()) > 0

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



def updateStrategyTable():
    with connect(
        host="localhost",
        user="root",
        password="94358857",
        database="trading"
    ) as connection, connection.cursor() as cursor:
        strategies = getStrategyInfoToTest()  
        optionsStrings = getAllOptionsToTest()

        # totalRuns = len(strategies)
        # run = 0

        for stratInfo in strategies:
            # run += 1
            # print(str(int(run*100.0/totalRuns)) + "%")
            for optionsString in optionsStrings:
                # if not strategyExistsInDB(
                #     stratInfo[0],
                #     stratInfo[1],
                #     stratInfo[2],
                #     stratInfo[3],
                #     optionsString,
                #     cursor):
                # ^ not needed if INSERT IGNORE works
                    insertStrategyIntoDB(
                        stratInfo[0],
                        stratInfo[1],
                        stratInfo[2],
                        stratInfo[3],
                        optionsString,
                        cursor)

            connection.commit()



def getStrategiesNotProcessed(ticker, datestr, cursor):
    cursor.execute("""
        SELECT *
        FROM trading.strategy as strategy
        WHERE NOT EXISTS (
            SELECT null
            FROM trading.backtest as backtest
            WHERE strategy.id = backtest.strategy_id
                AND backtest.ticker = %s
                AND backtest.date = %s
        )""",
        (ticker, datestr))
    return cursor.fetchall()


