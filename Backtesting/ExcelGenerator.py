import xlsxwriter 
import config 
from mysql.connector import connect, Error 
import CredentialsConfig.db_auth_config as db_auth_config

class ExcelGenerator: 

    def __init__(self, ticker):
        self.ticker = ticker 
        self.workbook = xlsxwriter.Workbook(config.records_directory + config.report_prefix + ticker + ".xslx")

    def run(self):
        print("Generating report for " + self.ticker)
        with connect(
            host=db_auth_config.host,
            user=db_auth_config.user,
            password=db_auth_config.password,
            database=db_auth_config.database
        ) as connection, connection.cursor() as cursor:
            # get top strategies ordered by highest profit (highest profit out of all options variations of the strategy)
            cursor.execute("\
                SELECT result.strat_name, result.aggregation, result.param1, result.param2 \
                FROM ( \
                    SELECT optComp.strat_name, optComp.aggregation, optComp.param1, optComp.param2, optComp.totalProfit \
                    FROM ( \
                        SELECT strategy.name as strat_name, strategy.aggregation, strategy.param1, strategy.param2, strategy.options_str, SUM(backtest.profit) as totalProfit \
                        FROM trading.backtest as backtest, trading.strategy as strategy \
                        WHERE  \
                            backtest.ticker = %s \
                            AND backtest.strategy_id = strategy.id \
                        GROUP BY strategy.id \
                        ORDER BY totalProfit DESC \
                    ) as optComp \
                    GROUP BY strat_name, aggregation, param1, param2 \
                    ORDER BY totalProfit DESC \
                ) as result \
                WHERE result.totalProfit > 0 \
                LIMIT 25" % \
                ("\"" + self.ticker + "\""))

            stratinfos = cursor.fetchall()

            # (name, aggregation, param1, param2, id)
            for stratinfo in stratinfos: 
                # create page for strategy
                worksheetName = str(stratinfo[1]) \
                    + " " + stratinfo[0] \
                    + "(" \
                    + ((stratinfo[2]) if stratinfo[2] != "None" else "")\
                    + (","+stratinfo[3] if stratinfo[3] != "None" else "")\
                    + ")"
                worksheet = self.workbook.add_worksheet(worksheetName)

                worksheet.set_column(0,0,10) # make A longer to see full date data 

                headings = ["Date", "Profit", "Trades"]
                data_row_start_char = "A"
                profit_column = "B"
                chart_start_column = "F"
                summary_column = "G"
                summary_row_start = 1
                data_insert_row = 1
                chart_height = 16

                # write sheet name for easier search:
                worksheet.write_row(
                    summary_column + str(summary_row_start),
                    ["Strategy:", worksheetName]
                )
                summary_row_start += 1

                # get top 10 options strings and respective strategy ids for 
                #   each strategy variation that was profitable, ordered by profit 
                cursor.execute("\
                    SELECT result.options_str, result.strategy_id \
                    FROM (\
                        SELECT strategy.options_str as options_str, strategy.id as strategy_id, SUM(backtest.profit) as totalProfit \
                        FROM trading.backtest as backtest, trading.strategy as strategy \
                        WHERE \
                            backtest.ticker = %s\
                            AND strategy.name = %s\
                            AND strategy.aggregation = %s\
                            AND strategy.param1 = %s\
                            AND strategy.param2 = %s\
                            AND strategy.id = backtest.strategy_id \
                        GROUP BY options_str\
                        ORDER BY totalProfit DESC\
                        ) as result \
                    WHERE result.totalProfit > 0\
                    LIMIT 10" % \
                    ("\"" + self.ticker + "\"", \
                    "\"" + stratinfo[0] + "\"", \
                    "\"" + str(stratinfo[1]) + "\"", \
                    "\"" + stratinfo[2] + "\"", \
                    "\"" + stratinfo[3] + "\"",))
                optionsStrings = cursor.fetchall()

                noneOption = "None"
                for optionsStringTuple in optionsStrings:
                    if optionsStringTuple[0] == noneOption: # TODO use optionsStringTuple instead of toSwitch
                        toSwitch = optionsStringTuple 
                        optionsStrings.remove(toSwitch)
                        optionsStrings.insert(0, toSwitch)

                # if (noneOption,) in optionsStrings:
                #     optionsStrings.remove((noneOption,))
                #     optionsStrings.insert(0, (noneOption,))

                for optionsStringTuple in optionsStrings:
                    optionsString = optionsStringTuple[0]
                    strategy_id = optionsStringTuple[1]

                    # get data for the strategy for each day
                    cursor.execute("\
                        SELECT date, profit, trades \
                        FROM trading.backtest \
                        WHERE \
                            strategy_id = %s\
                            AND ticker = %s\
                        ORDER BY date ASC" % \
                        (str(strategy_id), \
                        "\"" + self.ticker + "\""))

                    # = all entries for this strategy, ordered by date
                    backtestEntries = cursor.fetchall()
                    
                    ##############################
                    # write daily profit so far data  

                    profitCount = 0.00
                    tradesCount = 0

                    worksheet.write_row(
                        data_row_start_char + str(data_insert_row),
                        ["Options:", optionsString]
                    )
                    data_insert_row += 1

                    worksheet.write_row( # headers
                        data_row_start_char + str(data_insert_row),
                        headings)
                    data_insert_row += 1

                    data_start_row = data_insert_row 
                    worksheet.write_row( # init values 
                        data_row_start_char + str(data_insert_row),
                        ["0000-00-00", profitCount, tradesCount])
                    data_insert_row += 1

                    for entry in backtestEntries:
                        profitCount += float(entry[1])
                        tradesCount += int(entry[2])
                        worksheet.write_row(
                            data_row_start_char + str(data_insert_row),
                            [str(entry[0]), profitCount, tradesCount])
                        data_insert_row += 1

                    ##############################
                    # add summary data 

                    worksheet.write_row(
                        summary_column + str(summary_row_start),
                        ["Options:", optionsString]
                    )
                    summary_row_start += 1

                    worksheet.write_row(
                        summary_column + str(summary_row_start),
                        ["Profit:", profitCount]
                    )
                    summary_row_start += 1

                    worksheet.write_row(
                        summary_column + str(summary_row_start),
                        ["Trades:", tradesCount]
                    )
                    summary_row_start += 1

                    worksheet.write_row(
                        summary_column + str(summary_row_start),
                        ["~$/Week:", profitCount / (len(backtestEntries)/5.0)]
                    )
                    summary_row_start += 1

                    ##############################
                    # create chart from daily profit so far data:
                    chart = self.workbook.add_chart({'type': 'line'})
                    chart.add_series({
                        'values': "=\'" + worksheetName 
                                    + "\'!$" + profit_column 
                                    + "$" + str(data_start_row) 
                                    + ":$" + profit_column
                                    + "$" + str(data_insert_row-1)
                    })
                    chart.set_x_axis({'name': 'time (days)'})
                    chart.set_y_axis({'name': 'profit ($)'})
                    chart.set_style(10) # white outline and shadow 
                    worksheet.insert_chart(chart_start_column + str(summary_row_start), chart)

                    summary_row_start += chart_height
                    data_insert_row += 1

            self.workbook.close()



                



