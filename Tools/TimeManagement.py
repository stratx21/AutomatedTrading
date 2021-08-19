import config 
from datetime import datetime 

def getCurrentTime():
    return config.simulatingTimeStamp if config.simulating else datetime.now()

# check_time is before is_before
def isBeforeTime(check_time, is_before):
    return (check_time.hour < is_before.hour or (check_time.hour == is_before.hour and  check_time.minute <= is_before.minute))

# check_time is after is_after
def isAfterTime(check_time, is_after):
    return (is_after.hour < check_time.hour or (is_after.hour == check_time.hour and is_after.minute <= check_time.minute))

def currentTimeIsAfter(is_after):
    check_time = getCurrentTime()
    return check_time != None and isAfterTime(check_time, is_after)

def currentTimeIsBefore(is_before):
    check_time = getCurrentTime()
    return check_time != None and isBeforeTime(check_time, is_before)



def pastForceSellEOD():
    currentTimeIsAfter(config.AUTOSELL_FOR_CLOSE)

def withinBuyingTimeConstraint(start, stop):
    return currentTimeIsAfter(start) and currentTimeIsBefore(stop)

def withinSellingTimeConstraint():
    return currentTimeIsAfter(config.sell_start)

def marketIsOpen():
    return currentTimeIsAfter(config.MARKET_OPEN) and currentTimeIsBefore(config.MARKET_CLOSE)