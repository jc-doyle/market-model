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
        self.expected_price = model.market.current_price
        self.previous_return = 0
        self.horizon = random.randint(2, 50)
        self.wealth = wealth

    def generate_expectation(self):
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

        self.expected_price = expected_price + random.gauss(0, 0.15)

        return self.expected_price

    @property
    def current_price(self):
        return self.market.current_price

    @property
    def previous_price(self):
        return self.market.hist_price[-2]

    def generate_return(self):
        if (self.action == Action.BID):
            self.previous_return = self.current_price - self.previous_price
        elif (self.action == Action.OFFER):
            self.previous_return = self.previous_price - self.current_price
        elif self.action == Action.NOTHING:
            self.previous_return = 0

    def generate_action(self):
        if self.optimist and (self.expected_price > self.market.current_price):
            self.action = Action.BID
        elif self.pessimist and (self.expected_price < self.market.current_price):
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

    def update_wealth(self):
        self.wealth += self.previous_return

    def order(self):
        order = Order(self.unique_id, self.action)
        self.market.order(order)

    def step(self):
        # To account for the 1st time-step
        # Strucutred as sequential functions to indicate sequence of events
        try:
            self.generate_return()
            self.update_wealth()
            self.generate_expectation()
            self.generate_action()
            self.order()
        except:
            self.generate_expectation()
            self.generate_action()
            self.order()

    def advance(self):
        pass
