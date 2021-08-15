

def insertBacktest(cursor, ticker, stratinfo, datestr, profit, trades):

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
        stratinfo[5]))


    # cursor.execute("""
    #     INSERT INTO trading.backtest (ticker, strat_name, aggregation, param1, param2, options_str, date, profit, trades)
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
    #     (ticker, \
    #     stratinfo[0], \
    #     str(stratinfo[1]), \
    #     (str(stratinfo[2]) if stratinfo[2] != None else "None"), \
    #     (str(stratinfo[3]) if stratinfo[3] != None else "None"), \
    #     strategyKey,
    #     datestr, \
    #     strategies[strategyKey].profitSoFar, \
    #     strategies[strategyKey].tradesMade))


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


