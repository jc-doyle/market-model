import pandas as pd
import random
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
    def __init__(self, init_price, alpha, model):
        self.model = model
        self.ALPHA = alpha
        self.prices = [init_price]
        self.executed_bids = []
        self.executed_offers = []
        self.data = None

    @property
    def current_price(self):
        return self.prices[-1]

    def order(self, order: Order):
        if order.type == Action.BID:
            self.executed_bids.append(order)
        elif order.type == Action.OFFER:
            self.executed_offers.append(order)

    def ema(self, span):
        hist_series = pd.Series(self.prices)
        return hist_series.ewm(span=span, adjust=False).mean().iat[-1]

    def sma(self, k):
        cum_sum = 0
        if len(self.prices) < k:
            k = len(self.prices)

        for i, price in enumerate(list(reversed(self.prices))):
            if i == k:
                break
            cum_sum += price

        return cum_sum / k

    def update_price(self):
        # Determine Price for t+1
        excess_demand = len(self.executed_bids) - len(self.executed_offers)
        next_price = self.current_price + self.ALPHA * (excess_demand) + random.gauss(0, self.ALPHA/2)

        self.prices.append(next_price)

        self.executed_bids = []
        self.executed_offers = []

    def step(self):
        agents = self.model.schedule.agents

        if self.model.schedule.steps == 0:
            for agent in agents:
                agent.get_neighbours()

        if self.model.schedule.steps >= 1:
            for agent in agents:
                agent.switch()

        for agent in agents:
            agent.transact()

        self.model.data.collect(self.model)

        self.update_price()
        for agent in agents:
            agent.update_return(self.current_price, self.prices[-2])
            agent.generate_fitness()

        for agent in agents:
            agent.compare()


