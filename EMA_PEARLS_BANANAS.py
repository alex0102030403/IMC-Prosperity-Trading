from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd


# Constants
# MA_100POWER_BANANA = 40 / 100
# EMA_100POWER_BANANA = 60 / 100
# MA_POWER_PEARLS = 65 / 100
# EMA_POWER_PEARLS = 35 / 100
# MA_POWER = 40 / 100
# EMA_POWER = 60 / 100

pearls_q = []
bananas_q = []

EMA_yesterday_bananas = 0
EMA_yesterday_pearls = 0


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

            #Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                global EMA_yesterday_pearls

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid2 = max(order_depth.buy_orders.keys())
                best_bid_volume2 = order_depth.buy_orders[best_bid2]
                best_ask2 = min(order_depth.sell_orders.keys())
                best_ask_volume2 = order_depth.sell_orders[best_ask2]

                mid_price = (best_ask2 + best_bid2) / 2
                print("midPrice: ", mid_price)
                pearls_q.append(mid_price)

                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val

                average /= len(pearls_q)

                Close_today = mid_price;



                n = 25

                EMA_today = (Close_today * (2 / (n + 1))) + (EMA_yesterday_pearls * (1 - (2 / (n + 1))))
                EMA_yesterday_pearls = EMA_today

                average_ema = EMA_today

                if len(pearls_q) < 1000:
                    acceptable_price = average
                else:
                    acceptable_price = average_ema




                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!

                print("average is: ", acceptable_price)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
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
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'BANANAS':

                global EMA_yesterday_bananas

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid2 = max(order_depth.buy_orders.keys())
                best_bid_volume2 = order_depth.buy_orders[best_bid2]
                best_ask2 = min(order_depth.sell_orders.keys())
                best_ask_volume2 = order_depth.sell_orders[best_ask2]



                mid_price = (best_ask2 + best_bid2) / 2
                print("midPrice: ", mid_price)
                bananas_q.append(mid_price)
                if EMA_yesterday_bananas == 0:
                    EMA_yesterday_bananas = mid_price


                if len(bananas_q) > 100:
                    bananas_q.pop()

                average = 0
                for val in bananas_q:
                    average += val

                average /= len(bananas_q)


                # queue_df = pd.DataFrame(bananas_q)
                #
                # # compute exponential average using pandas ewm() function
                # exp_avg = queue_df.ewm(span=10).mean()

                Close_today = mid_price;



                n = 33

                EMA_today = (Close_today * (2 / (n + 1))) + (EMA_yesterday_bananas * (1 - (2 / (n + 1))))
                EMA_yesterday_bananas = EMA_today

                average_ema = EMA_today

                if len(bananas_q) < 10:
                    acceptable_price = average
                else:
                    acceptable_price = average_ema

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!

                print("average is: ", acceptable_price)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
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
                    best_bid = max(order_depth.buy_orders.keys())
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
