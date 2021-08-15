from Strategies.Strategy import Strategy
from Chart.RenkoStock import RenkoStock

class RenkoStrategy(Strategy):
    NAME = "RENKO_STRATEGY"

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)
        self.stock = RenkoStock(ticker, aggregation)
        self.stock.setNewOptCandleListener(self.optionManager.onNewCandle)



    