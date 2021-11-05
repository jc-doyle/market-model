import pandas as pd
from enum import Enum

class Action(Enum):
    BID = 0
    OFFER = 1
    NOTHING = 2

class Order:
    def __init__(self, id: int, type: Action):
        self.id = id
        self.type = type

class Market:
    def __init__(self, init_price, alpha) -> None:
        self.ALPHA = alpha
        self.current_price = init_price
        self.hist_price = [self.current_price]
        self.executed_bids = []
        self.executed_offers = []
        self.data = None

    def update(self):
        # Determine Price for t+1
        excess_demand = len(self.executed_bids) - len(self.executed_offers)
        self.current_price = (
            self.current_price
            + self.ALPHA * (excess_demand) / 2
             # + random.gauss(0, self.ALPHA)
        )

        self.hist_price.append(self.current_price)

        self.executed_bids = []
        self.executed_offers = []

    def order(self, order: Order):
        if order.type == Action.BID:
            self.executed_bids.append(order)
        elif order.type == Action.OFFER:
            self.executed_offers.append(order)

    def ema(self, span):
        hist_series = pd.Series(self.hist_price)
        return hist_series.ewm(span=span, adjust=False).mean().iat[-1]

    def sma(self, k):
        cum_sum = 0
        if len(self.hist_price) < k:
            k = len(self.hist_price)

        for i, price in enumerate(list(reversed(self.hist_price))):
            if i == k:
                break
            cum_sum += price

        return cum_sum / k

