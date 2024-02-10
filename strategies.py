### Goal: have a function that inherits the alpaca api and then
# takes in a symbol and looks at the previous data for that symbol
# to determine whether or not we should buy it!

from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import datetime
import os

load_dotenv()

APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_BASE_URL = os.getenv("APCA_API_BASE_URL")

api = tradeapi.REST()


def bollingerMA_API(apiObject, symbol):
    # Find short moving average:
    prices = []
    temp = api.get_barset(symbol, "1D", limit=15)
    for i in temp[symbol]:
        prices.append(i.c)
    short = np.mean(prices)

    # Find long moving average:
    prices = []
    temp = api.get_barset(symbol, "1D", limit=60)
    for i in temp[symbol]:
        prices.append(i.c)
    long = np.mean(prices)

    # Find bollinger bands:
    prices = []
    temp = api.get_barset(symbol, "1D", limit=20)
    for i in temp[symbol]:
        prices.append(i.c)
    avg = np.mean(prices)
    std = np.std(prices)
    upper = avg + (2 * std)
    lower = avg - (2 * std)
    upSafe = avg + (1 * std)
    lowSafe = avg - (1 * std)

    # Get the current price:
    current = api.get_barset(symbol, "1D", limit=1)
    price = current[symbol][0].c

    # Now we check to see if we should buy or sell:
    if price > upper:
        # sell
        # print('Above bollinger')
        return -1
    elif price < lower:
        # buy
        # print('Below bollinger')
        return 1
    elif price > lowSafe and price < upSafe and short - long < 0:
        # sell
        # print('MA reasons')
        return -1
    elif price > lowSafe and price < upSafe and short - long > 0:
        # buy
        # print('MA reasons')
        return 1
    else:
        # do nothing
        return 0


def bollingerMA_Backtest(symbol, data):
    # Find short moving average:
    prices = []
    for i in range(-15, 0):
        prices.append(data[i])
    short = np.mean(prices)

    # Find long moving average:
    prices = []
    for i in range(-60, 0):
        prices.append(data[i])
    long = np.mean(prices)

    # Find bollinger bands:
    prices = []
    for i in range(-20, 0):
        prices.append(data[i])
    avg = np.mean(prices)
    std = np.std(prices)
    upper = avg + (2 * std)
    lower = avg - (2 * std)
    upSafe = avg + (1 * std)
    lowSafe = avg - (1 * std)

    # Get the current price:
    price = data[-1]

    # Now we check to see if we should buy or sell:
    if price > upper:
        # sell
        # print('Above bollinger')
        return -1
    elif price < lower:
        # buy
        # print('Below bollinger')
        return 1
    elif price > lowSafe and price < upSafe and short - long < 0:
        # sell
        # print('MA reasons')
        return -1
    elif price > lowSafe and price < upSafe and short - long > 0:
        # buy
        # print('MA reasons')
        return 1
    else:
        # do nothing
        return 0


if __name__ == "__main__":
    print(bollingerMA_API(api, "SNAP"))
    temp = api.get_barset("SNAP", "1D", limit=1000)
    print(len(temp["SNAP"]))
