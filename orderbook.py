from collections import defaultdict
from enum import Enum
from queue import Queue
from market import Order



class OrderBook:
    def __init__(self) -> None:
        self.bids = defaultdict(Queue)
        self.offers = defaultdict(Queue)

    @property
    def highest_bid(self):
        if self.bids:
            return max(price for price in self.bids.keys() if self.bids[price].empty() is not True)
        else:
            return None

    @property
    def lowest_offer(self):
        if self.offers:
            return min(price for price in self.offers.keys() if self.offers[price].empty() is not True)
        else:
            return float('inf')

    def order(self, order:Order):
        if order.type == Type.BID:
            self.bids[order.price].put(order)
        elif order.type == Type.OFFER:
            self.offers[order.price].put(order)

    def match(self, order:Order):
        if order.type == Type.BID:
            if order.price >= self.lowest_offer:
                matched_bid = self.bids[order.price].get()
                matched_offer = self.offers[self.lowest_offer].get()
                print('MATCH BID {0} = OFFER {1}'.format(matched_bid, matched_offer))
                return matched_bid, matched_offer
            else:
                print("No Match")
                return None, None
        if order.type == Type.OFFER:
            if not self.bids[order.price].empty():
                matched_bid = self.bids[order.price].get()
                matched_offer = self.offers[order.price].get()
                print('MATCH BID {0} = OFFER {1}'.format(matched_bid, matched_offer))

            else:
                print("No Match")

    def match_all(self):
        executed_bids = []
        executed_offers = []
        bids = self.bids
        for _, orders in bids.items():
            for order in list(orders.queue):
                bids,offers = self.match(order)
                if bids != None: executed_bids.append(bids)
                if offers != None: executed_offers.append(offers)
        
        return executed_bids, executed_offers

    def show(self):
        print('---BID---')
        for price,orders in self.bids.items():
            for order in list(orders.queue):
                print(order)
        print('--OFFER--')
        for price,orders in self.offers.items():
            for order in list(orders.queue):
                print(order)

if __name__ == "__main__":
    book = OrderBook()

    orders = [
        Order(1,5,Type.OFFER),
        Order(2,5,Type.OFFER),
        Order(3,6,Type.OFFER),
        Order(4,6,Type.OFFER),
        Order(4,7,Type.OFFER),
        Order(5,4,Type.BID),
        Order(6,4,Type.BID),
        Order(7,4,Type.BID),
        Order(8,5,Type.BID),
        Order(9,6,Type.BID),
        Order(9,7,Type.BID),
        Order(10,4,Type.OFFER),
    ]

    for order in orders:
        book.order(order)

    bids, offers = book.match_all()
    print(bids)
    print(offers)
    print('{0} : {1}'.format(book.highest_bid, book.lowest_offer))
    book.show()
