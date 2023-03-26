from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
import pandas as pd

Last_Short = 0
Last_Upwards = 0

Shortam = 0
Upwards = 0

pearls_q = []
bananas_q = []
coconuts_q = []

EMA_20_Colada_yesterday = []
EMA_20_Colada_today = 0

EMA_100_Colada_yesterday = []
EMA_100_Colada_today = 0

Signals_Colada = []

EMA_yesterday_coconuts = 0

EMA_yesterday_bananas = 5000
EMA_yesterday_pearls = 10000

trend_calculator_q = []
trend_calculator_algo = []

EMA_small_coconut = 0
EMA_big_coconut = 0
EMA_DAYS_SMALL = 5
EMA_DAYS_BIG = 15
last_coco_trend = -1
last_deal_price_coco = 0

EMA_small_sight = 0
EMA_big_sight = 0
last_sight_trend = 0
EMA_DAYS_SMALL_SIGHT = 4
EMA_DAYS_BIG_SIGHT = 150
EMA_gear = 0


def ema_calc_coco(close_today, n):
    global EMA_small_coconut
    global EMA_big_coconut
    if n == EMA_DAYS_SMALL:
        yesterday_EMA = EMA_small_coconut
    elif n == EMA_DAYS_BIG:
        yesterday_EMA = EMA_big_coconut
    else:
        return -1
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
    EMA_today = (close_today * (2 / (n + 1))) + (yesterday_EMA * (1 - (2 / (n + 1))))
    return EMA_today


def ema_calc_gear(close_today, n):
    global EMA_gear
    yesterday_EMA = EMA_gear
    EMA_today = (close_today * (2 / (n + 1))) + (yesterday_EMA * (1 - (2 / (n + 1))))
    return EMA_today


def ema_calc(close_today, n):
    global EMA_yesterday_bananas
    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_bananas * (1 - (2 / (n + 1))))
    EMA_yesterday_bananas = EMA_today
    return EMA_today


def ema_calc_colada(close_today, n):
    global EMA_yesterday_coconuts
    EMA_today = (close_today * (2 / (n + 1))) + (EMA_yesterday_coconuts * (1 - (2 / (n + 1))))
    EMA_yesterday_coconuts = EMA_today
    return EMA_today


# def trend_calculator(average, allTimeAverage):
#     global trend_calculator_q
#     global trend_calculator_algo
#     sume = 0
#     if len(trend_calculator_q) < 10:
#         trend_calculator_q.append(average)
#     else:
#         trend_calculator_q.pop()
#     for el in trend_calculator_q:
#         sume += el
#
#     avg = sume / len(trend_calculator_q)
#     trend_calculator_algo.append(avg)
#     if len(trend_calculator_algo) > 10:
#         trend_calculator_algo.pop()
#
#     avgAns = avg
#
#     return allTimeAverage - avgAns
#

class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        for product in state.order_depths.keys():  # Iterate over all the keys (the available products) contained in the order dephts
            if product == 'NO PEARLS':  # Check if the current product is the 'PEARLS' product, only then run the order logic
                global EMA_yesterday_pearls
                order_depth: OrderDepth = state.order_depths[
                    product]  # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                orders: list[Order] = []  # Initialize the list of Orders to be sent as an empty list
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())  # print("bb ", best_bid, "ba", best_ask)
                mid_price = (best_ask + best_bid) / 2  # print("midPrice: ", mid_price)

                pearls_q.append(mid_price)
                if len(pearls_q) > 100:
                    pearls_q.pop()

                average = 0
                for val in pearls_q:
                    average += val
                average /= len(pearls_q)
                # Define a fair value for the PEARLS.
                acceptable_price = int(average)  # print("fair price (average): ", acceptable_price)
                position = state.position.get(product, 0)
                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price
                    asks_lower_than_acceptable_price = []
                    for price, volume in order_depth.sell_orders.items():
                        if price < acceptable_price:
                            asks_lower_than_acceptable_price.append(
                                (price, volume))  # print("Possible buy deal found: ", volume, "@", price)
                    asks_lower_than_acceptable_price.sort()
                    for price, volume in asks_lower_than_acceptable_price:
                        max_volume = min(-volume, 20 - position)
                        print("BUY ", max_volume, "@", price)
                        orders.append(Order(product, price, max_volume))
                        position += max_volume

                if len(order_depth.buy_orders) != 0:
                    bids_higher_than_acceptable_price = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bids_higher_than_acceptable_price.append(
                                (price, volume))  # print("Possible sell deal found: ", volume, "@", price)
                    bids_higher_than_acceptable_price.sort(reverse=True)
                    for price, volume in bids_higher_than_acceptable_price:
                        max_volume = min(volume, 20 + position)
                        print("SELL ", -max_volume, "@", price)
                        orders.append(Order(product, price, -max_volume))
                        position -= max_volume
                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'NO BANANAS':
                global EMA_yesterday_bananas
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                bananas_q.append(mid_price)
                if len(bananas_q) > 100:
                    bananas_q.pop()
                if EMA_yesterday_bananas == 0:
                    EMA_yesterday_bananas = mid_price

                average = 0
                for val in bananas_q:
                    average += val
                average /= len(bananas_q)

                Close_today = mid_price
                EMA100_Banane = ema_calc(Close_today, 100)
                EMA5_Banane = ema_calc(Close_today, 5)
                # EMA50_Banane = ema_calc(Close_today, 50)
                # EMA25_Banane = ema_calc(Close_today, 25)
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
                    asks_lower_than_acceptable_price.sort()
                    theoretical_max_position = 20

                    for price, volume in asks_lower_than_acceptable_price:
                        max_volume = min(-volume, theoretical_max_position - position)
                        print("BUY ", max_volume, "@", price)
                        orders.append(Order(product, price, max_volume))
                        position += max_volume

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
                    bids_higher_than_acceptable_price.sort(reverse=True)

                    theoretical_max_position = 20
                    for price, volume in bids_higher_than_acceptable_price:
                        max_volume = min(volume, theoretical_max_position + position)
                        print("SELL ", -max_volume, "@", price)
                        orders.append(Order(product, price, -max_volume))
                        position -= max_volume
                # Add all the above the orders to the result dict
                result[product] = orders

            if product == "NO COCONUTS":
                global EMA_small_coconut
                global EMA_big_coconut
                global last_coco_trend
                global last_deal_price_coco
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                position = state.position.get(product, 0)

                if EMA_small_coconut == 0:
                    EMA_small_coconut = mid_price
                    EMA_big_coconut = mid_price
                    last_deal_price_coco = mid_price
                EMA_big_coconut = ema_calc_coco(mid_price, EMA_DAYS_BIG)
                EMA_small_coconut = ema_calc_coco(mid_price, EMA_DAYS_SMALL)
                current_trend = last_coco_trend
                # current_trend = 1 if (EMA_small_coconut - EMA_big_coconut) > 1 else -1
                if (EMA_small_coconut - EMA_big_coconut) > 0.2:
                    current_trend = 1
                elif (EMA_small_coconut - EMA_big_coconut) < -0.2:
                    current_trend = -1

                if current_trend == last_coco_trend:
                    # place orders as maker
                    print("sEMA ", EMA_small_coconut, "        BEMA ", EMA_big_coconut, " --> ", current_trend)
                elif current_trend == 1:
                    print("# take buy order")
                    oportunity = (last_deal_price_coco - mid_price) / 30
                    position_allowance = 600 - position
                    wanted_volume = oportunity * position_allowance
                    if len(order_depth.sell_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_ask = min(order_depth.sell_orders.keys())
                        print("bb ", best_bid, "ba", best_ask)
                        asks_lower_than_acceptable_price = []
                        for price, volume in order_depth.sell_orders.items():
                            asks_lower_than_acceptable_price.append((price, volume))
                        # Sort all the available sell orders by their price
                        asks_lower_than_acceptable_price.sort()
                        for price, volume in asks_lower_than_acceptable_price:
                            max_volume = min(-volume, wanted_volume)
                            print("BUY ", max_volume, "@", price)
                            orders.append(Order(product, price, max_volume))
                            last_deal_price_coco = price
                            wanted_volume -= max_volume
                            if wanted_volume == 0:
                                break
                            else:
                                print("inca un buy")

                else:
                    print("# take sell order")
                    oportunity = -(last_deal_price_coco - mid_price) / 30
                    position_allowance = 600 + position
                    wanted_volume = oportunity * position_allowance
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_ask = min(order_depth.sell_orders.keys())
                        print("bb ", best_bid, "ba", best_ask)
                        bids_higher_than_acceptable_price = []
                        for price, volume in order_depth.buy_orders.items():
                            bids_higher_than_acceptable_price.append((price, volume))
                        # Sort all the available sell orders by their price
                        bids_higher_than_acceptable_price.sort(reverse=True)
                        for price, volume in bids_higher_than_acceptable_price:
                            max_volume = min(volume, wanted_volume)
                            print("SELL ", -max_volume, "@", price)
                            orders.append(Order(product, price, -max_volume))
                            last_deal_price_coco = price
                            wanted_volume -= max_volume
                            if wanted_volume == 0:
                                break
                            else:
                                print("inca un sell")
                last_coco_trend = current_trend
                # Add all the above the orders to the result dict
                result[product] = orders

            if product == 'NO PINA_COLADAS':

                global EMA_yesterday_coconuts
                global AllTimesAverage_q

                global Signals_Colada

                global EMA_20_Colada_yesterday
                global EMA_20_Colada_today

                global EMA_100_Colada_yesterday
                global EMA_100_Colada_today

                global coconuts_q

                global Last_Short
                global Last_Upwards

                global Shortam
                global Upwards

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                best_bid2 = max(order_depth.buy_orders.keys())
                best_ask2 = min(order_depth.sell_orders.keys())

                mid_price = (best_ask2 + best_bid2) / 2

                # AverageAllTime = sumAllTime / impart

                # SOS = trend_calculator(mid_price, AverageAllTime)
                # letsSee = trend_calculator(mid_price, AverageAllTime)
                # # print("TREND CALCULATOR : ",letsSee)

                # print("midPrice: ", mid_price)
                coconuts_q.append(mid_price)
                if EMA_yesterday_coconuts == 0:
                    EMA_yesterday_coconuts = mid_price

                if len(coconuts_q) > 100:
                    coconuts_q.pop()

                average = 0
                for val in coconuts_q:
                    average += val

                average /= len(coconuts_q)

                Close_today = mid_price

                average_ema = ema_calc_colada(Close_today, 25)

                acceptable_price = average_ema

                EMA_20_Colada_yesterday.append(ema_calc_colada(Close_today, 20))
                EMA_100_Colada_yesterday.append(ema_calc_colada(Close_today, 100))

                if ema_calc_colada(Close_today, 20) > ema_calc_colada(Close_today, 50):
                    Signals_Colada.append(1)

                else:
                    Signals_Colada.append(-1)

                Shortam = 0
                Upwards = 0

                # for i , element in enumerate(Signals_Colada):
                #     if len(Signals_Colada) > 1:
                #         next_element = Signals_Colada[i+1] if i < len(Signals_Colada)-1 else None
                #         # print("Curent element ",element)
                #         # print("Next element ", next_element)
                #         if element == -1 and next_element == 1:
                #
                #             Upwards = 1
                #         elif element == 1 and next_element == -1:
                #             Shortam = -1

                if (len(Signals_Colada) > 2):
                    if (Signals_Colada[len(Signals_Colada) - 2] == -1 and Signals_Colada[len(Signals_Colada) - 1] == 1):
                        Upwards = 1
                    elif (Signals_Colada[len(Signals_Colada) - 2] == 1 and Signals_Colada[
                        len(Signals_Colada) - 1] == -1):
                        Shortam = -1

                print("SHORTU LOCAL--  ", Shortam, "UPU LOCAL--  ", Upwards)

                if (Upwards == 1 and Shortam == 0):
                    Last_Upwards = 1
                    Last_Short = 0

                if (Upwards == 0 and Shortam == -1):
                    Last_Short = -1
                    Last_Upwards = 0

                # if(Shortam == 0 and Upwards == 1 and Last_Upwards ==1 and Last_Short == 0):
                #     Last_Upwards = 1
                #
                # if (Shortam == -1 and Upwards == 0 and Last_Upwards == 0 and Last_Short == -1):
                #     Last_Short = -1
                #
                # if (Shortam == -1 and Upwards == 0 and Last_Upwards == 1 and Last_Short == 0):
                #     Last_Short = -1

                # if(Last_Short == -1 and Shortam == 0):
                #     Last_Short = 0
                # elif(Last_Short == 0 and Shortam == -1):
                #     Last_Short = -1
                # elif(Last_Short == -1 and Shortam == -1):
                #     Last_Short = -1
                #
                #
                # if(Last_Upwards == 1 and Upwards == 0):
                #     Last_Upwards = 0
                # elif(Last_Upwards == 0 and Upwards ==1):
                #     Last_Upwards = 1
                # elif(Last_Upwards == 1 and Upwards ==1):
                #     Last_Upwards = 1

                print(Last_Short, "  -LAST SHORT-  ", Last_Upwards, "  -LAST UP-  ")

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    bestAsks2 = []
                    # asta inca nu i folosita
                    for key, value in order_depth.buy_orders.items():
                        if key < acceptable_price:
                            bestAsks2.append((key, value))

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price and Last_Short == -1:
                        orders.append(Order(product, best_ask, -best_ask_volume))
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(acceptable_price - best_ask) + "x", best_ask)
                        # for key,value in bestAsks2:
                        #     orders.append(Order(product, key, -value))
                    elif best_ask < acceptable_price and Last_Upwards == 1:
                        for key, value in bestAsks2:
                            orders.append(Order(product, key, -value))

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]

                    # asta inca nu i folosita
                    bestAsks = []
                    for key, value in order_depth.buy_orders.items():
                        if key > acceptable_price:
                            bestAsks.append((key, value))

                    if best_bid > acceptable_price and Last_Short == -1:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)

                        # acCompute = trend_calculator(mid_price, AverageAllTime)
                        # print("Algo Compute", acCompute)
                        #
                        for key, value in bestAsks:
                            orders.append(Order(product, key, -value))

                        # orders.append(Order(product, best_bid, -best_bid_volume))
                    elif best_bid > acceptable_price and Last_Upwards == 1:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

            if product == "DIVING_GEAR":
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
                EMA_gear = ema_calc_gear(mid_price, 8)

                super_price=EMA_gear * 1.0025
                max_volume = min(10, 20 + position)
                orders.append(Order(product, super_price, -max_volume))
                super_price=EMA_gear * 0.9975
                max_volume = min(10, 20 - position)
                orders.append(Order(product, super_price, max_volume))

                print("BIG EMA ",EMA_big_sight, "     small ema", EMA_small_sight )
                current_trend = last_sight_trend
                if (EMA_small_sight - EMA_big_sight) > 1.25:
                    current_trend = 1
                elif (EMA_small_sight - EMA_big_sight) < -1.25:
                    current_trend = -1

                if current_trend == 1:
                    print("# take buy order")
                    acceptable_price = EMA_gear * 1.0015
                    if len(order_depth.sell_orders) > 0:
                        if best_ask < acceptable_price:
                            best_ask_volume = order_depth.sell_orders[best_ask]
                            max_volume = min(-best_ask_volume, 20 - position)
                            print("Diving gear: ", "BUY ", max_volume, "@", best_ask)
                            orders.append(Order(product, best_ask, max_volume))
                    if len(order_depth.buy_orders) > 0:
                        if best_bid > acceptable_price:
                            best_bid_volume = order_depth.buy_orders[best_bid]
                            max_volume = min(best_bid_volume, 20 + position)
                            print("Diving gear: ", "SELL ", -max_volume, "@", best_bid)
                            orders.append(Order(product, best_bid, -max_volume))
                elif current_trend == -1:
                    print("# take sell order")
                    acceptable_price = EMA_gear * 0.9985
                    if len(order_depth.sell_orders) > 0:
                        if best_ask < acceptable_price:
                            best_ask_volume = order_depth.sell_orders[best_ask]
                            max_volume = min(-best_ask_volume, 20 - position)
                            print("Diving gear: ", "BUY ", max_volume, "@", best_ask)
                            orders.append(Order(product, best_ask, max_volume))
                    if len(order_depth.buy_orders) > 0:
                        if best_bid > acceptable_price:
                            best_bid_volume = order_depth.buy_orders[best_bid]
                            max_volume = min(best_bid_volume, 20 + position)
                            print("Diving gear: ", "SELL ", -max_volume, "@", best_bid)
                            orders.append(Order(product, best_bid, -max_volume))

                last_sight_trend = current_trend
                # Add all the above the orders to the result dict
                result[product] = orders

            # Return the dict of orders
            # These possibly contain buy or sell orders for PEARLS
            # Depending on the logic above
        return result
