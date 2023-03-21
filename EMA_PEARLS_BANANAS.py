from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order



# Constants
# MA_100POWER_BANANA = 40 / 100
# EMA_100POWER_BANANA = 60 / 100
# MA_POWER_PEARLS = 65 / 100
# EMA_POWER_PEARLS = 35 / 100
# MA_POWER = 40 / 100
# EMA_POWER = 60 / 100

EMA25_Banane = 0
EMA50_Banane = 0
EMA100_Banane = 0
EMA5_Banane = 0
EMA10_Banane = 0

pearls_q = []
bananas_q = []

EMA_yesterday_bananas = 0
EMA_yesterday_pearls = 0

trend_calculator_q = []
trend_calculator_algo = []

AllTimesAverage_q = []

sumAllTime = 0
timestamp = 0


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
                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
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


                # Add all the above the orders to the result dict
                result[product] = orders

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':
                global EMA_yesterday_bananas
                global AllTimesAverage_q
                global sumAllTime
                global timestamp
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())

                mid_price = (best_ask + best_bid) / 2

                timestamp += 1
                sumAllTime += mid_price
                AverageAllTime = sumAllTime / timestamp

                letsSee = trend_calculator(mid_price, AverageAllTime)
                # print("TREND CALCULATOR : ", letsSee)

                # print("midPrice: ", mid_price)
                bananas_q.append(mid_price)
                if EMA_yesterday_bananas == 0:
                    EMA_yesterday_bananas = mid_price

                if len(bananas_q) > 100:
                    bananas_q.pop()

                average = 0
                for val in bananas_q:
                    average += val

                average /= len(bananas_q)

                Close_today = mid_price

                average_ema = ema_calc(Close_today, 25)
                EMA100_Banane = ema_calc(Close_today,100)
                EMA5_Banane = ema_calc(Close_today,5)
                EMA50_Banane = ema_calc(Close_today,50)
                EMA10_Banane = ema_calc(Close_today,10)
                print(EMA100_Banane, "ASTA II EMA 100 ",EMA5_Banane ,"Asta ii ema 5")


                if len(bananas_q) < 15:
                    acceptable_price = average
                else:
                    acceptable_price = EMA5_Banane
                    #acceptable_price = (EMA100_Banane+EMA5_Banane)/2

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!

                # print("average is: ", acceptable_price)

                inventory = state.position.get(product, 0)

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    bestAsks2 = []
                    # asta inca nu i folosita
                    for price, volume in order_depth.buy_orders.items():
                        if price < acceptable_price:
                            bestAsks2.append((price, volume))

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(acceptable_price - best_ask) + "x", best_ask)
                        # for key, value in bestAsks2:
                        #     orders.append(Order(product,key,-value))
                        if inventory - best_ask_volume > 20:
                            newVolumeBanane = (inventory - best_ask_volume)-20
                            orders.append(Order(product,best_ask,newVolumeBanane))
                        else:
                            orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it find the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium

                if len(order_depth.buy_orders) != 0:
                    # asta inca nu i folosita
                    bestAsks = []
                    for price, volume in order_depth.buy_orders.items():
                        if price > acceptable_price:
                            bestAsks.append((price, volume))

                    if best_bid > acceptable_price:
                        print("SELL", str(acceptable_price - best_bid) + "x", best_bid)

                        acCompute = trend_calculator(mid_price,AverageAllTime)
                        #print("Algo Compute", acCompute)
                        # for key,value in bestAsks:
                        #     orders.append(Order(product,key,-value))
                        if inventory - best_bid_volume < -20:
                            newVolumeSell = (inventory - best_bid_volume) + 20
                            orders.append(Order(product,best_bid,newVolumeSell))
                        else:
                            orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above the orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
