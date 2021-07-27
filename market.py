import math

class Market:
    def __init__(self, init_price) -> None:
        self.current_price = init_price
        self.hist_price = []
        self.buy_orders = []
        self.sell_orders = []

    def buy(self, amount: int):
        self.buy_orders.append(amount)

    def sell(self, amount: int):
        self.sell_orders.append(amount)

    def get_price(self):
        return self.current_price

    def update_price(self):
        excess_demand = sum(self.buy_orders) - sum(self.sell_orders)
        self.hist_price.append(self.current_price)
        self.current_price = self.current_price*math.exp(excess_demand/2000)
        self.buy_orders = []
        self.sell_orders = []
