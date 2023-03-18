from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd

# Constants
MA_100POWER_BANANA = 40 / 100
EMA_100POWER_BANANA = 60 / 100
MA_100POWER_PEARLS = 65 / 100
EMA_100POWER_PEARLS = 35 / 100
pearls_q = []
bananas_q = []

last_banana_price = 0
last_pearl_price = 0
pearls_EMA_yesterday = 0
banana_EMA_yesterday = 0

class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                global pearls_EMA_yesterday
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                global last_pearl_price
                best_bid = max(order_depth.buy_orders.keys(), default=last_pearl_price)
                best_ask = min(order_depth.sell_orders.keys(), default=last_pearl_price)

                mid_price = (best_ask + best_bid) / 2
                print("midPrice: ", mid_price)
                pearls_q.append(mid_price)
                last_pearl_price = mid_price
                if pearls_EMA_yesterday == 0:
                    pearls_EMA_yesterday = mid_price
                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val
                average /= len(pearls_q)

                close_today = mid_price
                n = 50
                average_ema = (close_today * (2 / (n + 1))) + (pearls_EMA_yesterday * (1 - (2 / (n + 1))))
                pearls_EMA_yesterday = average_ema
                print("ema is: ", average_ema)

                # Define a fair value for the PEARLS.
                acceptable_price = average * MA_100POWER_PEARLS + average_ema * EMA_100POWER_PEARLS
                print("acceptable_price is: ", acceptable_price)
                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(acceptable_price - best_ask) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                global last_banana_price
                global banana_EMA_yesterday
                best_bid = max(order_depth.buy_orders.keys(), default=last_banana_price)
                best_ask = min(order_depth.sell_orders.keys(), default=last_banana_price)

                mid_price = (best_ask + best_bid) / 2
                print("midPrice: ", mid_price)
                bananas_q.append(mid_price)
                last_banana_price = mid_price
                if banana_EMA_yesterday == 0:
                    banana_EMA_yesterday = mid_price
                if len(bananas_q) > 100:
                    bananas_q.pop()

                average = 0
                for val in bananas_q:
                    average += val
                average /= len(bananas_q)

                close_today = mid_price
                n = 35
                average_ema = (close_today * (2 / (n + 1))) + (banana_EMA_yesterday * (1 - (2 / (n + 1))))
                banana_EMA_yesterday = average_ema
                print("ema is: ", average_ema)

                # Define a fair value for the BANANA.
                acceptable_price = average * MA_100POWER_BANANA + average_ema * EMA_100POWER_BANANA
                print("average is: ", acceptable_price)
                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(acceptable_price - best_ask) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
