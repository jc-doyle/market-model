import random
from enum import Enum

from mesa import Agent

from market import Order
from market import Action


class Type(Enum):
    OPTIMIST = 0
    PESSIMIST = 1
    RANDOM = 2


class Agent(Agent):
    def __init__(self, id, model, type, wealth):
        super().__init__(id, model)
        self.market = model.market
        self.type = type
        self.action = Action.NOTHING
        self.exp = model.market.current_price
        self.horizon = random.randint(2, 50)
        self.wealth = wealth
        self.periodic_return = []

    def expected_price(self):
        react_coeff = random.uniform(0, 1)
        price_ema = self.market.sma(self.horizon)
        if self.optimist:
            expected_price = self.current_price + react_coeff * (
                self.current_price - price_ema
            )
        else:
            expected_price = self.current_price - react_coeff * (
                self.current_price - price_ema
            )

        self.exp = expected_price + random.gauss(0, 0.15)

        return self.exp

    @property
    def current_price(self):
        return self.market.current_price

    @property
    def previous_price(self):
        return self.market.hist_price[-2]

    def generate_action(self):
        if self.optimist and (self.expected_price() > self.market.current_price):
            self.action =Action.BID
        elif self.pessimist and (self.expected_price() < self.market.current_price):
            self.action = Action.OFFER
        elif self.type == Type.RANDOM:
            self.action = Action(random.randint(0, 2))
        else:
            self.action = Action.NOTHING

    @property
    def optimist(self):
        if self.type == Type.OPTIMIST:
            return True
        else:
            return False

    @property
    def pessimist(self):
        if self.type == Type.PESSIMIST:
            return True
        else:
            return False

    def update_return(self):
        if self.action == Action.BID:
            self.wealth += self.current_price - self.previous_price
        elif self.action == Action.OFFER:
            self.wealth += self.previous_price - self.current_price

    def order(self):
        order = Order(self.unique_id, self.action)
        self.market.order(order)

    def step(self):
        self.generate_action()
        self.order()

    def advance(self):
        pass
