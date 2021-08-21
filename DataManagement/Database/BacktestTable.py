
# unused ? 
def insertBacktest(cursor, ticker, stratinfo, datestr, profit, trades, optionsStr):

    cursor.execute("""
        INSERT INTO trading.backtest
        SELECT %s, strategy.id, %s, %s, %s
        FROM trading.strategy as strategy
        WHERE 
            strategy.name = %s 
            AND strategy.aggregation = %s 
            AND strategy.param1 = %s 
            AND strategy.param2 = %s 
            AND strategy.options_str = %s""",
        (ticker, \
        datestr, \
        profit, \
        trades, \
        stratinfo[0], \
        stratinfo[1], \
        (str(stratinfo[2]) if stratinfo[2] != None else "None"), \
        (str(stratinfo[3]) if stratinfo[3] != None else "None"), \
        optionsStr))


def getBacktestResultsDbCount(cursor, ticker, stratinfo, optionsString, datestr):
    cursor.execute("\
        SELECT * \
        FROM trading.backtest as backtest, trading.strategy as strategy \
        WHERE \
            backtest.ticker = %s\
            AND backtest.strategy_id = strategy.id \
            AND strategy.name = %s\
            AND strategy.aggregation = %s\
            AND strategy.param1  = %s \
            AND strategy.param2 = %s\
            AND strategy.options_str = %s\
            AND backtest.date = %s" % \
        ("\"" + ticker + "\"", \
        "\"" + stratinfo[0] + "\"", \
        "\"" + str(stratinfo[1]) + "\"", \
        "\"" + (str(stratinfo[2]) if stratinfo[2] != None else "None") + "\"", \
        "\"" + (str(stratinfo[3]) if stratinfo[3] != None else "None") + "\"", \
        "\"" + optionsString + "\"", \
        "\"" + datestr + "\""))

    return len(cursor.fetchall())

def deleteByStrategyId(cursor, strategyId):
    cursor.execute("""DELETE FROM trading.backtest WHERE strategy_id = %s""", (strategyId, ))

class BacktestBatchInsertManager:
    VALUES_BUFFER_SIZE = 500
    QUERY_INITIAL = "INSERT INTO trading.backtest (ticker, strategy_id, date, profit, trades) VALUES "

    def __init__(self, connection, cursor):
        self.valuesCount = 0
        self.cursor = cursor 
        self.connection = connection 

        self.resetQuery()

    def insert(self, ticker, strategy_id, date, profit, trades):
        if self.valuesCount > 0:
            self.query += ","
        self.query += " (\"" + ticker + "\", " + str(strategy_id) + ", \"" + date + "\", " + str(profit) + ", " + str(trades) + ")"
        self.valuesCount += 1

        if self.valuesCount >= BacktestBatchInsertManager.VALUES_BUFFER_SIZE:
            self.runQuery()

    def runQuery(self):
        if self.cursor != None and self.valuesCount > 0:
            self.cursor.execute(self.query)
            self.connection.commit()
            self.resetQuery()

    def resetQuery(self):
        self.query = BacktestBatchInsertManager.QUERY_INITIAL
        self.valuesCount = 0

    def flush(self):
        self.runQuery()



    
