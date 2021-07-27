from mesa import Agent
import random

class agent(Agent):
    def __init__(self, id , model, wealth):
        super().__init__(id, model)
        self.wealth = wealth
        self.market = self.model.market
        self.stocks = 1

    def gen_expectation(self):
        self.market.get_price()
        self.order_signal = random.randint(0,2)

    def order(self):
        self.order_amount = random.randint(0,2)
        current_price = self.market.get_price()

        # Buy Signal
        if (self.order_signal == 0) & (self.wealth > current_price):
            self.market.buy(self.order_amount)
            self.wealth = self.wealth - self.order_amount*current_price

        # Sell Signal
        elif (self.order_signal == 1):
            self.market.sell(self.order_amount)

        # Hold Signal (Pass)
        else:
            pass

    def step(self):
        self.gen_expectation()
        self.order()
