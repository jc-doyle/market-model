from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

import networkx as nx

from market import Market
from agent import Agent
from agent import Type


class MarketModel(Model):
    def __init__(
        self, agents, non_random, price, alpha, beta, gamma, rho, network, convergence
    ):
        self.num_agents = agents
        self.non_random = non_random
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.market = Market(price, alpha)
        self.running = True
        self.convergence = convergence
        self.network = self.create_network(network)

        # Initialize Agents
        for id in range(self.num_agents):
            if id < (self.num_agents * self.non_random / 2):
                a = Agent(id, self, Type.OPTIMIST, beta, gamma, rho)
            elif id < (self.num_agents * self.non_random):
                a = Agent(id, self, Type.PESSIMIST, beta, gamma, rho)
            else:
                a = Agent(id, self, Type.RANDOM, beta, gamma, rho)

            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

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
                "Action": "action",
                "Price": "current_price",
                "Expectation": "expected_price",
                "Exp Return": "expected_return",
                "Fitness": "strategy_fitness",
                "Previous Return": "previous_return",
                "opt": "optimist_mean",
                "pess": "pessimist_mean",
                "prob": "opt_prob",
                "rng": "rng",
            },
        )

        self.test = DataCollector(
            agent_reporters={
                "Price-test": "price_test",
            },
        )

    def create_network(self, input):
        n = int(self.num_agents * self.non_random)
        if input[0].lower() == "regular" or input[0].lower() == "random":
            return nx.random_regular_graph(input[1], n)
        elif input[0].lower() == "scalefree":
            return nx.powerlaw_cluster_graph(n, input[1], input[2])
        elif input[0].lower() == "smallworld":
            return nx.powerlaw_cluster_graph(n, input[1], input[2])
        elif input[0].lower() == "barabasi":
            return nx.barabasi_albert_graph(n, input[1])
        elif input[0].lower() == "caveman":
            return nx.caveman_graph(input[1], input[2])
        elif input[0].lower() == "none":
            return nx.random_regular_graph(0, n)

    def step(self):
        self.market.update()
        self.schedule.step()
        self.data.collect(self)
        self.test.collect(self)
        self.market.data = self.data.get_agent_vars_dataframe()
