from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

import networkx as nx
import pandas as pd

from market import Market
from agent import MarketAgent, Type
from schedule import Schedule


class MarketModel(Model):
    def __init__(
        self, steps, agents, non_random, price, alpha, beta, gamma, rho, network, convergence
    ):
        self.STEPS = steps
        self.NUM_AGENTS = agents
        self.NON_RANDOM = non_random
        self.init_price = price

        self.market = Market(price, alpha, self)
        self.running = True
        self.convergence = convergence
        self.network = self.create_network(network)

        self.schedule = BaseScheduler(self)

        # Initialize Agents
        for id in range(self.NUM_AGENTS):
            if id < (self.NUM_AGENTS * self.NON_RANDOM / 2):
                a = MarketAgent(id, self, Type.OPTIMIST, beta, gamma, rho)
            elif id < (self.NUM_AGENTS * self.NON_RANDOM):
                a = MarketAgent(id, self, Type.PESSIMIST, beta, gamma, rho)
            else:
                a = MarketAgent(id, self, Type.RANDOM, beta, gamma, rho)

            self.schedule.add(a)

        # Data Collection Variables
        self.data = DataCollector(
            model_reporters={
                "Price": lambda m: m.market.current_price,
                "Bids": lambda m: len(m.market.executed_bids),
                "Offers": lambda m: len(m.market.executed_offers),
            },
            agent_reporters={
                "Trading Type": "type.name",
                "Horizon": "horizon",
                "Action": "action.name",
                "Price": "current_price",
                "Prev. Return": "previous_return",
                "Expectation": "expected_price",
                "Exp Return": "expected_return",
                "Fitness": "fitness",
                "opt": "optimist_mean",
                "pess": "pessimist_mean",
                "prob": "opt_prob",
                "rng": "rng",
            },
        )


    def create_network(self, input):
        n = int(self.NUM_AGENTS * self.NON_RANDOM)
        if input[0].lower() == "regular" or input[0].lower() == "random":
            return nx.random_regular_graph(input[1], n)
        elif input[0].lower() == "scalefree":
            return nx.powerlaw_cluster_graph(n, input[1], input[2])
        elif input[0].lower() == "smallworld":
            return nx.powerlaw_cluster_graph(n, input[1], input[2])
        elif input[0].lower() == "barabasi":
            return nx.barabasi_albert_graph(n, input[1])
        elif input[0].lower() == "none":
            return nx.random_regular_graph(0, n)

    def step(self):
        self.market.step()
        self.schedule.step()

    def run(self):
        i = 0
        self.market.prices = [self.init_price]
        while i < self.STEPS:
            self.step()
            i += 1

