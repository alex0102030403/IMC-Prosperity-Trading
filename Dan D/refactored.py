from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

pearls_q = []
bananas_q = []
EMA25_bananas = 5000  # should be zero and initialised at first iteration

EMA_small_sight = 0
EMA_big_sight = 0
last_sight_trend = 0
EMA_DAYS_SMALL_SIGHT = 4
EMA_DAYS_BIG_SIGHT = 150
EMA_gear = 0

EMA_Berries = 0
QUEUE_Berries = []


def general_ema(close_today, n, yesterday_EMA):
    EMA_today = (close_today * (2 / (n + 1))) + (yesterday_EMA * (1 - (2 / (n + 1))))
    return EMA_today


def ema_calc_sight(close_today, n):
    global EMA_small_sight
    global EMA_big_sight
    if n == EMA_DAYS_SMALL_SIGHT:
        yesterday_EMA = EMA_small_sight
    elif n == EMA_DAYS_BIG_SIGHT:
        yesterday_EMA = EMA_big_sight
    else:
        return -1
    return general_ema(close_today, n, yesterday_EMA)


def ema_calc_gear(close_today):
    global EMA_gear
    return general_ema(close_today, n=8, yesterday_EMA=EMA_gear)


def ema_calc_bananas(close_today):
    global EMA25_bananas
    return general_ema(close_today, n=25, yesterday_EMA=EMA25_bananas)


def ema_calc_berries(close_today):
    global EMA_Berries
    return general_ema(close_today, n=30, yesterday_EMA=EMA_Berries)


class Trader:
    def take_all_orders_with_acceptable_price(self, acceptable_price, order_depth, position, product,
                                              max_position):
        # Initialize the list of Orders to be returned as an empty list
        orders: list[Order] = []

        # If statement checks if there are any SELL orders in the PEARLS market
        if len(order_depth.sell_orders) > 0 and position < max_position:
            # Sort all the available sell orders by their price
            asks_lower_than_acceptable_price = []
            for price, volume in order_depth.sell_orders.items():
                if price < acceptable_price:
                    # print("Possible buy deal found: ", volume, "@", price)
                    asks_lower_than_acceptable_price.append((price, volume))
            asks_lower_than_acceptable_price.sort()
            for price, volume in asks_lower_than_acceptable_price:
                new_volume = min(-volume, max_position - position)
                print("BUY ", new_volume, "@", price)
                orders.append(Order(product, price, new_volume))
                position += new_volume
        if len(order_depth.buy_orders) != 0 and position > -max_position:
            bids_higher_than_acceptable_price = []
            for price, volume in order_depth.buy_orders.items():
                if price > acceptable_price:
                    bids_higher_than_acceptable_price.append((price, volume))
                    # print("Possible sell deal found: ", volume, "@", price)
            bids_higher_than_acceptable_price.sort(reverse=True)
            for price, volume in bids_higher_than_acceptable_price:
                new_volume = min(volume, max_position + position)
                print("SELL ", -new_volume, "@", price)
                orders.append(Order(product, price, -new_volume))
                position -= new_volume

        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            if product == 'PEARLS':
                print("PERLE")
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                position = state.position.get(product, 0)
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                # print("bb ", best_bid, "ba", best_ask)

                mid_price = (best_ask + best_bid) / 2
                # print("midPrice: ", mid_price)
                pearls_q.append(mid_price)
                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val
                average /= len(pearls_q)
                # Define a fair value for the PEARLS.
                acceptable_price = int(average)
                # print("fair price (average): ", acceptable_price)

                # Add all the above the orders to the result dict
                result[product] = self.take_all_orders_with_acceptable_price(
                    acceptable_price, order_depth, position, product, max_position=20)
            if product == 'BANANAS':
                print("BANANA")
                global EMA25_bananas
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                position = state.position.get(product, 0)
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                bananas_q.append(mid_price)
                if len(bananas_q) > 20:
                    bananas_q.pop()
                # if EMA25_bananas == 0:
                #     EMA25_bananas = mid_price

                average = 0
                for val in bananas_q:
                    average += val
                average /= len(bananas_q)
                EMA25_bananas = ema_calc_bananas(mid_price)

                if len(bananas_q) < 15:
                    acceptable_price = average
                else:
                    acceptable_price = EMA25_bananas

                result[product] = self.take_all_orders_with_acceptable_price(
                    acceptable_price, order_depth, position, product, max_position=20)
            if product == 'NO BERRIES':
                print("BERRIES")
                global QUEUE_Berries
                global EMA_Berries

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                QUEUE_Berries.append(mid_price)
                if len(QUEUE_Berries) > 100:
                    QUEUE_Berries.pop()
                if EMA_Berries == 0:
                    EMA_Berries = mid_price

                average = 0
                for val in QUEUE_Berries:
                    average += val
                average /= len(QUEUE_Berries)

                Close_today = mid_price
                EMA_Berries = ema_calc_berries(Close_today)

                if len(QUEUE_Berries) < 15:
                    acceptable_price = average
                else:
                    acceptable_price = EMA_Berries

                position = state.position.get(product, 0)
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < 3960:
                            # print("Possible buy deal found: ", volume, "@", price)
                            asks_lower_than_acceptable_price.append((price, volume))

                    for price, volume in asks_lower_than_acceptable_price:
                        new_volume = min(-volume, 20 - position)
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
                        if price > 3985:
                            bids_higher_than_acceptable_price.append((price, -volume))

                    for price, volume in bids_higher_than_acceptable_price:
                        new_volume = min(volume, 20 + position)
                        print("SELL ", -new_volume, "@", price)
                        orders.append(Order(product, price, -volume))

                # Add all the above the orders to the result dict
                result[product] = orders
            if product == "DIVING_GEAR":
                print("DIVING")
                global EMA_small_sight
                global EMA_big_sight
                global last_sight_trend
                global EMA_gear
                sights = state.observations["DOLPHIN_SIGHTINGS"]
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                position = state.position.get(product, 0)

                if EMA_small_sight == 0:
                    EMA_small_sight = sights
                    EMA_big_sight = sights
                    EMA_gear = mid_price

                EMA_big_sight = ema_calc_sight(sights, EMA_DAYS_BIG_SIGHT)
                EMA_small_sight = ema_calc_sight(sights, EMA_DAYS_SMALL_SIGHT)
                EMA_gear = ema_calc_gear(mid_price)

                # place some orders that would be a best deal for us. Maybe there is a bot care pune botul
                super_price = EMA_gear * 1.0025
                max_volume = min(10, 20 + position)
                orders.append(Order(product, super_price, -max_volume))
                super_price = EMA_gear * 0.9975
                max_volume = min(10, 20 - position)
                orders.append(Order(product, super_price, max_volume))

                print("BIG EMA ", EMA_big_sight, "     small ema", EMA_small_sight)
                current_trend = last_sight_trend
                if (EMA_small_sight - EMA_big_sight) > 1.25:
                    current_trend = 1
                    print("# take buy order")
                    acceptable_price = EMA_gear * 1.0015
                elif (EMA_small_sight - EMA_big_sight) < -1.25:
                    current_trend = -1
                    print("# take sell order")
                    acceptable_price = EMA_gear * 0.9985

                if current_trend == 1 or current_trend == -1:
                    max_position = 20  # CHANGE TO 50
                    orders = orders + self.take_all_orders_with_acceptable_price(
                        acceptable_price, order_depth, position, product, max_position=20)  # CHANGE TO 50

                last_sight_trend = current_trend
                # Add all the above the orders to the result dict
                result[product] = orders

        return result
