from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from market import Market

from agent import agent


class myModel(Model):
    def __init__(self, agents=4, wealth=100, price=20):
        self.num_agents = agents
        self.schedule = RandomActivation(self)
        self.market = Market(price)

        for id in range(self.num_agents):
            a = agent(id, self, wealth)
            self.schedule.add(a)

        self.data = DataCollector(
            model_reporters={"Price": lambda m: m.market.current_price},
            agent_reporters={"Wealth": "wealth"}
        )
    
    def step(self):
        self.data.collect(self)
        self.schedule.step()
        self.market.update_price()


if __name__ == "__main__":
    model = myModel()

    for i in range(15):
        model.step()

    print(model.data.get_agent_vars_dataframe())
