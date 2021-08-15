from Strategies.Strategy import Strategy 
from Chart.RangeStock import RangeStock

class RangeStrategy(Strategy):
    NAME = "RANGE_STRATEGY"

    def __init__(self, ticker, aggregation):
        super().__init__(ticker, aggregation)
        self.stock = RangeStock(ticker, aggregation)
        self.stock.setNewOptCandleListener(self.optionManager.onNewCandle)