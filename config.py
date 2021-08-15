from datetime import datetime, time  



# messy way of doing it, but best for actual application 
simulating = False 
simulatingTimeStamp = None 

csvBacktestLogEnabled = False

callback_url = "http://localhost"
config_json_file = "CredentialsConfig/config_account.json"
token_config_file = "CredentialsConfig/token.config.json"
token_config_file_jh2 = "CredentialsConfig/token_jh2.config.json"
report_prefix = "Report_"
records_directory = "Records/"
def get_trade_records_directory():
    return "Records/Trades/" if not simulating else "Records/Trades/Backtesting/"

#NOTE : if market is closed on a Monday, Tuesday won't get enough data
days_of_history_to_get = 1

TICKERS_TO_AVG_BA = ["VDE", "GUSH", "LABU", "LABD", "UVXY", "UCO"]
TICKERS_TO_USE_ASK= []

# TODO remove the isJH2 stuff everywhere if the same token can be used twice 
def getTokenConfigFile(isJH2 = False):
    return token_config_file if not isJH2 else token_config_file_jh2

MARKET_OPEN = time(8, 30)
MARKET_CLOSE= time(15, 00)

AUTOSELL_FOR_CLOSE = time(14,55)

# time constraints: 
buy_start = time( 8, 35)
buy_stop  = time(14, 45)

buy_start_specified = {
    "GUSH": time( 8, 40), # massive BA till then or later 
    "VDE":  time( 8, 45), # jumps a good bit until then 
}

buy_stop_specified = {
    "GUSH": time(12, 00),
    "VDE":  buy_stop,
}

def getBuyStart(ticker):
    if ticker in buy_start_specified:
        return buy_start_specified[ticker]
    return buy_start

def getBuyStop(ticker):
    if ticker in buy_stop_specified:
        return buy_stop_specified[ticker]
    return buy_stop


sell_start = buy_start 


refresh_token_minutes = 25
refresh_token_expires_days = 90

#ms delay if pipe has no data to check again in ms 
DELAY_PIPE_CHECKING = 100 

# check_time is before is_before
def isBeforeTime(check_time, is_before):
    return (check_time.hour < is_before.hour or (check_time.hour == is_before.hour and  check_time.minute <= is_before.minute))

# check_time is after is_after
def isAfterTime(check_time, is_after):
    return (is_after.hour < check_time.hour or (is_after.hour == check_time.hour and is_after.minute <= check_time.minute))


def marketIsOpen():
    if not simulating:
        check_time = datetime.now()
        return isAfterTime(check_time, MARKET_OPEN) and isBeforeTime(check_time, MARKET_CLOSE)
    else:
        simulatingTimeStamp != None \
            and isAfterTime(simulatingTimeStamp, MARKET_OPEN) and isBeforeTime(simulatingTimeStamp, MARKET_CLOSE)



def withinBuyingTimeConstraint(start, stop):
    if not simulating:
        check_time = datetime.now()
        return isAfterTime(check_time, start) and isBeforeTime(check_time, stop) 
    else:
        return simulatingTimeStamp != None \
            and isAfterTime(simulatingTimeStamp, start) and isBeforeTime(simulatingTimeStamp, stop)

def withinSellingTimeConstraint():
    if not simulating:
        check_time = datetime.now()
        return isAfterTime(check_time, sell_start)
    else:
        return isAfterTime(simulatingTimeStamp, sell_start)