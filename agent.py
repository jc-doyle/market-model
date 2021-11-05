import random
import statistics
import math
from enum import Enum

from mesa import Agent

from market import Order
from market import Action


class Type(Enum):
    OPTIMIST = 0
    PESSIMIST = 1
    RANDOM = 2


class Agent(Agent):
    def __init__(self, id, model, type, beta, gamma, rho):
        super().__init__(id, model)
        self.market = model.market
        self.memory = random.uniform(0, 1)
        self.type = type
        self.optimist_mean = 0
        self.pessimist_mean = 0
        self.opt_prob = 0
        self.rng = 0
        self.action = Action.NOTHING
        self.expected_price = model.market.current_price
        self.previous_return = 0
        self.horizon = random.randint(2, gamma)
        self.beta = beta
        self.rho = rho

    @property
    def current_price(self):
        return self.market.current_price

    @property
    def previous_price(self):
        return self.market.hist_price[-2]

    @property
    def price_test(self):
        return self.market.data.xs(self.unique_id, level=1)[-1:]['Price'].values[0]

    @property
    def expected_return(self):
        if self.optimist:
            return self.expected_price - self.current_price
        else:
            return self.current_price - self.expected_price

    @property
    def strategy_fitness(self):
        return (
            self.memory * self.expected_return
            + (1 - self.memory) * self.previous_return
        )

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

    @property
    def random(self):
        if self.type == Type.RANDOM:
            return True
        else:
            return False

    def generate_expectation(self):
        reeact_coeff = random.gauss(0.5, 0.1)
        price_sma = self.market.sma(self.horizon)
        expected_change = self.current_price - price_sma

        if self.optimist:
            expected_price = self.current_price + reeact_coeff * (expected_change)
        else:
            expected_price = self.current_price - 2*reeact_coeff * (expected_change)

        self.expected_price = expected_price + random.gauss(0, self.beta)

    def generate_return(self):
        if self.action == Action.BID:
            self.previous_return = self.current_price - self.previous_price
        elif self.action == Action.OFFER:
            self.previous_return = self.previous_price - self.current_price
        elif self.action == Action.NOTHING:
            self.previous_return = 0

    def generate_action(self):
        if self.optimist and (self.expected_price > self.market.current_price):
            self.action = Action.BID
        elif self.pessimist and (self.expected_price < self.market.current_price):
            self.action = Action.OFFER
        elif self.random:
            self.action = Action(random.randint(0, 2))
        else:
            self.action = Action.NOTHING

    def order(self):
        order = Order(self.unique_id, self.action)
        self.market.order(order)

    def compare_strategy(self):
        self.optimist_max_horizon = 0
        self.pessimist_max_horizon = 0
        self.optimist_fitness = []
        self.pessimist_fitness = []
        for other_id in self.model.network[self.unique_id]:
            other = self.model.schedule.agents[other_id]
            if other.pessimist:
                if other.strategy_fitness > self.pessimist_max_horizon:
                    self.pessimist_max_horizon = other.horizon
                self.pessimist_fitness.append(other.strategy_fitness)
            elif other.optimist:
                if other.strategy_fitness > self.optimist_max_horizon:
                    self.optimist_max_horizon = other.horizon
                self.optimist_fitness.append(other.strategy_fitness)

        # Mean fitness of neighbours
        if len(self.optimist_fitness) > 0:
            self.optimist_mean = statistics.mean(self.optimist_fitness)
        else:
            self.optimist_mean = 0

        if len(self.pessimist_fitness) > 0:
            self.pessimist_mean = statistics.mean(self.pessimist_fitness)
        else:
            self.pessimist_mean = 0

        # Logit Binary Choice model
        self.opt_prob = math.exp(self.optimist_mean * self.rho) / (
            math.exp(self.pessimist_mean * self.rho)
            + math.exp(self.optimist_mean * self.rho)
        )

        self.rng = random.uniform(0, 1)

        # Decision assignment (Control for no neigbors)
        if not (self.pessimist_fitness == [] and self.optimist_fitness == []):
            if self.opt_prob > self.rng:
                self.type = Type.OPTIMIST
                if self.model.convergence and self.optimist_max_horizon > 0:
                    self.horizon = self.optimist_max_horizon
            else:
                self.type = Type.PESSIMIST
                if self.model.convergence and self.pessimist_max_horizon > 0:
                    self.horizon = self.pessimist_max_horizon

    def step(self):
        # To account for the 1st time-step
        # Strucutred as sequential functions to better indicate sequence of events
        try:
            self.generate_return()
            self.generate_expectation()
            self.generate_action()
        except:
            self.generate_expectation()
            self.generate_action()

    def advance(self):
        self.order()
        if not self.random:
            self.compare_strategy()
