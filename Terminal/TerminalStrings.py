import Terminal.Colors as color

EXIT = "exit"
STOP = "stop"
START = "start"
ADD = "add"
REMOVE = "remove"
REMOVE_SHORTHAND = "rm"
DISABLE = "disable"
ENABLE = "enable"
SHOW = "show"
STATUS = "status"
REFRESH_TOKEN = "refresh"
STRATS = "strats"
OPT = "opt"
HELP = "help"

SET = "set"
STREAM = "stream"
TICKER = 'ticker'

GUI = "gui"


HELP_OUTPUT = "[help] " + EXIT + "\n" + "[help] " + STOP + "\n" + "[help] " + START + "\n" + "[help] " + ADD + "\n" + "[help] " + REMOVE + "\n" + "[help] " + DISABLE + "\n" + "[help] " + ENABLE + "\n" + "[help] " + SHOW + "\n" + "[help] " + STATUS + "\n" + "[help] " + REFRESH_TOKEN + "\n[help] " + STRATS + "\n[help] " + OPT + "\n[help] " + HELP + "\n"

# NC = No Color
SYS_MESSAGE_NC = "[sys message]" 
WARNING_NC = "[WARNING]" 
ERROR_NC = "[ERROR]" 
TRADE_NOTIFICATION_NC = "[TRADE NOTIFICATION]" 
STRATEGY_NC = "[strategy]" 
SIMULATED_NC = "[SIMULATED]" 

SYS_MESSAGE =        color.WARNING + SYS_MESSAGE_NC + color.ENDC
WARNING =            color.WARNING + WARNING_NC + color.ENDC
ERROR =              color.FAIL    + ERROR_NC + color.ENDC
TRADE_NOTIFICATION = color.OKGREEN + TRADE_NOTIFICATION_NC + color.ENDC
STRATEGY =           color.OKCYAN  + STRATEGY_NC  + color.ENDC
SIMULATED =          color.WARNING + SIMULATED_NC + color.ENDC


def getStrategyPrintFormat(ticker, strat, aggregation, optionalArgument1 = None, optionalArgument2 = None):
    return ("["+ticker.upper()+"]: ("+aggregation+","+strat + ((","+str(optionalArgument1)) if optionalArgument1 != None else "") + ((","+str(optionalArgument2)) if (optionalArgument2 != None) else (""))+")")

