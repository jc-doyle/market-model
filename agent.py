import random
import statistics
import math
from networkx.classes.function import neighbors
import pandas as pd
import numpy as np
from enum import Enum

from mesa import Agent

from market import Order
from market import Action


class Type(Enum):
    OPTIMIST = 0
    PESSIMIST = 1
    RANDOM = 2


class MarketAgent(Agent):
    def __init__(self, id, model, type, beta, gamma, rho):
        super().__init__(id, model)
        self.market = model.market

        self.memory = random.randint(2, 10)
        self.beta = beta
        self.rho = rho
        self.horizon = random.randint(2, gamma)
        self.expected_price = model.market.current_price


        if type != Type.RANDOM:
            self.types = np.zeros(model.STEPS, dtype='byte')
            self.types[0] = type.value
        else:
            self.types = Type.RANDOM.value*np.ones(model.STEPS, dtype='byte')

        self.actions = np.zeros(model.STEPS, dtype='float64')
        self.returns = np.zeros(model.STEPS, dtype='float64')

        self.fitness = 0
        self.optimist_mean = 0
        self.pessimist_mean = 0
        self.neighbours = []
        self.opt_prob = 0
        self.rng = 0

    @property
    def time(self):
        return self.model.schedule.time

    @property
    def current_price(self):
        return self.market.current_price

    @property
    def previous_return(self):
        return self.returns[self.time]

    @property
    def type(self):
        return Type(self.types[self.time])

    @property
    def action(self):
        return Action(self.actions[self.time])


    @property
    def expected_return(self):
        if self.type is Type.OPTIMIST:
            return self.expected_price - self.current_price
        else:
            return self.current_price - self.expected_price

    @property
    def random(self):
        return self.types[self.time] == Type.RANDOM.value

    def get_neighbours(self):
        neighbours = []
        if not self.random:
            for other_id in self.model.network[self.unique_id]:
                neighbours.append(self.model.schedule.agents[other_id])
                
        self.neighbours = neighbours


    def generate_expectation(self):
        react_coeff = random.gauss(0.5, 0.1)
        price_sma = self.market.ema(self.horizon)
        expected_change = self.current_price - price_sma

        if self.type is Type.OPTIMIST:
            expected_price = self.current_price + react_coeff * (expected_change)
        else:
            expected_price = self.current_price - react_coeff * (expected_change)

        self.expected_price = expected_price + random.gauss(0, self.beta)

    def update_return(self, current_price, previous_price):
        if self.action == Action.BID:
            self.returns[self.time] = current_price - previous_price
        elif self.action == Action.OFFER:
            self.returns[self.time] = previous_price - current_price
        elif self.action == Action.NOTHING:
            self.returns[self.time] = 0

    def generate_fitness(self):
        if not self.random:
            types = self.types[:self.time]
            returns = self.returns[:self.time]
            type_returns = returns[types == Type(self.types[self.time]).value]

            if type_returns.size > 0:
                self.fitness = type_returns[::-1][:random.randint(1,5)].mean()
            else:
                self.fitness = 0

    def generate_action(self):
        action = Action.NOTHING

        if self.type is Type.OPTIMIST:
            if self.expected_price > self.market.current_price:
                action = Action.BID
        elif self.type is Type.PESSIMIST:
            if self.expected_price < self.market.current_price:
                action = Action.OFFER
        elif self.random:
            action = Action(random.randint(0, 2))

        self.actions[self.time] = action.value

    def order(self):
        order = Order(self.unique_id, self.action)
        self.market.order(order)

    def compare(self):
        optimists = []
        pessimists = []
        for a in self.neighbours:
            if a.fitness != None:
                if Type(a.types[self.time]) == Type.OPTIMIST:
                    optimists.append(a.fitness)
                if Type(a.types[self.time]) == Type.PESSIMIST:
                    pessimists.append(a.fitness)

        if len(optimists) > 0:
            self.optimist_mean = statistics.mean(optimists)
        else:
            self.optimist_mean = 0

        if len(pessimists) > 0:
            self.pessimist_mean = statistics.mean(pessimists)
        else:
            self.pessimist_mean = 0

                
    def transact(self):
        self.generate_expectation()
        self.generate_action()
        self.order()

    def switch(self):
        self.types[self.time] = self.types[self.time-1]


        if not ((self.random) or (self.neighbours == [])):
            if self.type == Type.OPTIMIST:
                self.optimist_mean = (self.fitness + self.optimist_mean)/2
            else:
                self.pessimist_mean = (self.fitness + self.pessimist_mean)/2

            # Logit Binary Choice model
            self.opt_prob = math.exp(self.optimist_mean * self.rho) / (
                math.exp(self.pessimist_mean * self.rho)
                + math.exp(self.optimist_mean * self.rho)
            )

            self.rng = random.uniform(0, 1)

            # Decision assignment (Control for no neighbours)
            if self.pessimist_mean != 0 or self.optimist_mean != 0:
                if self.opt_prob > self.rng:
                    self.types[self.time] = Type.OPTIMIST.value
                else:
                    self.types[self.time] = Type.PESSIMIST.value
