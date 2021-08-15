from Terminal import Colors 

def printStrategyNewCandle(ticker, newCandle):
        print(Colors.getDirectionColor(newCandle.close > newCandle.open) + ticker + Colors.ENDC, " open:", "{:.2f}".format(newCandle.open), " close:", "{:.2f}".format(newCandle.close), " low:", "{:.2f}".format(newCandle.low), " high:", "{:.2f}".format(newCandle.high))


