from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

from scipy import stats
from scipy.stats import powerlaw

from market import Market
from agent import Agent
from agent import Type


class MarketModel(Model):
    def __init__(self, agents, price):
        self.num_agents = agents
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(10, 10, True)
        self.market = Market(price)
        self.running = True

        # Initialize Agents
        a = 1.5
        pow = powerlaw(a, scale=70, loc=30)

        for id in range(self.num_agents):
            wealth = pow.rvs()
            if id < 2:
                a = Agent(id, self, Type.OPTIMIST, wealth)
            elif id < 4:
                a = Agent(id, self, Type.PESSIMIST, wealth)
            else:
                a = Agent(id, self, Type.RANDOM, wealth)

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
                "Type": "type",
                "Wealth": "wealth",
                "Price": "current_price",
                "Expectation": "exp",
                "Horizon": "horizon",
                "Action": "action",
                "Optimist": "optimist",
                "Optimist": "pessimist",
            },
        )

    def step(self):
        self.schedule.step()
        self.market.update()
        self.data.collect(self)
