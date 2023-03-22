from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

pearls_q = []
bananas_q = []

EMA_yesterday_bananas = 5000
EMA_yesterday_pearls = 10000

trend_calculator_q = []
trend_calculator_algo = []

sumAllTime = 0
timestamp = 0

best_ever_banana_deal_spread = 0.001


def ema_calc(close_today, n):
    global EMA_yesterday_bananas
    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_bananas * (1 - (2 / (n + 1))))
    EMA_yesterday_bananas = EMA_today
    return EMA_today


def trend_calculator(average, allTimeAverage):
    global trend_calculator_q
    global trend_calculator_algo
    sume = 0
    if len(trend_calculator_q) < 10:
        trend_calculator_q.append(average)
    else:
        trend_calculator_q.pop()
    for el in trend_calculator_q:
        sume += el

    avg = sume / len(trend_calculator_q)
    trend_calculator_algo.append(avg)
    if len(trend_calculator_algo) > 10:
        trend_calculator_algo.pop()

    avgAns = avg

    return allTimeAverage - avgAns


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
                global EMA_yesterday_pearls
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                print("bb ", best_bid, "ba", best_ask)

                mid_price = (best_ask + best_bid) / 2
                print("midPrice: ", mid_price)
                pearls_q.append(mid_price)
                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val
                average /= len(pearls_q)
                # Define a fair value for the PEARLS.
                acceptable_price = int(average)
                print("fair price (average): ", acceptable_price)
                position = state.position.get(product, 0)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < acceptable_price:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))
                    asks_lower_than_acceptable_price.sort()
                    for price, volume in asks_lower_than_acceptable_price:
                        new_volume = min(-volume, 20 - position)
                        print("BUY ", new_volume, "@", price)
                        orders.append(Order(product, price, new_volume))
                        position += new_volume

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bids_higher_than_acceptable_price.append((price, volume))
                            # print("Possible sell deal found: ", volume, "@", price)
                    bids_higher_than_acceptable_price.sort(reverse=True)
                    for price, volume in bids_higher_than_acceptable_price:
                        new_volume = min(volume, 20 + position)
                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -new_volume))
                        position -= new_volume

                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':
                global EMA_yesterday_bananas
                global sumAllTime
                global timestamp
                global best_ever_banana_deal_spread
                best_ever_banana_deal_spread *= 0.8
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                bananas_q.append(mid_price)
                if len(bananas_q) > 100:
                    bananas_q.pop()
                if EMA_yesterday_bananas == 0:
                    EMA_yesterday_bananas = mid_price

                timestamp += 1
                sumAllTime += mid_price
                AverageAllTime = sumAllTime / timestamp

                average = 0
                for val in bananas_q:
                    average += val
                average /= len(bananas_q)

                Close_today = mid_price
                EMA100_Banane = ema_calc(Close_today, 100)
                EMA5_Banane = ema_calc(Close_today, 5)
                # EMA50_Banane = ema_calc(Close_today, 50)
                EMA25_Banane = ema_calc(Close_today, 25)
                # EMA10_Banane = ema_calc(Close_today, 10)

                if len(bananas_q) < 15:
                    acceptable_price = average
                else:
                    # acceptable_price = EMA5_Banane
                    acceptable_price = (EMA100_Banane + EMA5_Banane) / 2
                    # acceptable_price = EMA25_Banane

                position = state.position.get(product, 0)
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < acceptable_price:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))
                            if acceptable_price - price > best_ever_banana_deal_spread:
                                best_ever_banana_deal_spread = acceptable_price - price
                    asks_lower_than_acceptable_price.sort()
                    theoretical_max_position = min(
                        20 / (best_ever_banana_deal_spread / 4) * (acceptable_price - best_ask), 20)
                    theoretical_max_position = 20

                    for price, volume in asks_lower_than_acceptable_price:
                        new_volume = min(-volume, theoretical_max_position - position)
                        print("BUY ", new_volume, "@", price)
                        orders.append(Order(product, price, new_volume))
                        position += new_volume

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bids_higher_than_acceptable_price.append((price, volume))
                            # print("Possible sell deal found: ", volume, "@", price)
                            if price - acceptable_price > best_ever_banana_deal_spread:
                                best_ever_banana_deal_spread = price - acceptable_price
                    bids_higher_than_acceptable_price.sort(reverse=True)
                    print("best_ever_banana_deal_spread: ", best_ever_banana_deal_spread)
                    theoretical_max_position = min(
                        20 / (best_ever_banana_deal_spread / 4) * (best_bid - acceptable_price), 20)

                    theoretical_max_position = 20
                    for price, volume in bids_higher_than_acceptable_price:
                        new_volume = min(volume, theoretical_max_position + position)
                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -new_volume))
                        position -= new_volume
                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
