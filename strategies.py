### Goal: have a function that inherits the alpaca api and then
# takes in a symbol and looks at the previous data for that symbol
# to determine whether or not we should buy it!

from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import datetime
import logging
import os

# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

load_dotenv()

APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

api = tradeapi.REST()

def get_bars_list(symbol, length):
    now = datetime.datetime.now()
    now = now - datetime.timedelta(days=1)

    prices = []
    temp = pd.DataFrame({})
    i = length

    while temp.shape[0] < length:
        temp = api.get_bars(
            symbol, 
            TimeFrame.Day, 
            start=(
                now - datetime.timedelta(days=i)
                ).strftime(
                    '%Y-%m-%d'
                    ),
            end=now.strftime('%Y-%m-%d'), 
            adjustment='raw',
            limit=length
            ).df
        i += 1
    return temp

def bollingerMA_API(apiObject, symbol):
    # Find short moving average
    logging.debug(f'Obtaining short MA for symbol {symbol}')
    short_ = get_bars_list(symbol, 15)['close'].mean()
    logging.info(f'Short MA for {symbol}: {short_}')

    # Find long moving average:
    logging.debug(f'Obtaining long MA for symbol {symbol}')
    long_ = get_bars_list(symbol, 30)['close'].mean()
    logging.info(f'Long MA for {symbol}: {long_}')

    # Find bollinger bands:
    logging.debug(f'Obtaining Bollinger Bands for symbol {symbol}')
    avg = get_bars_list(symbol, 20)['close'].mean()
    std = get_bars_list(symbol, 20)['close'].std()
    upper = avg + (2 * std)
    lower = avg - (2 * std)
    upSafe = avg + (1 * std)
    lowSafe = avg - (1 * std)

    # Get the current price:
    logging.debug(f'Obtaining current price for symbol {symbol}')
    price = get_bars_list(symbol, 1)['close'].mean()

    # Now we check to see if we should buy or sell:
    logging.debug(f'Determining buy/sell for symbol {symbol}...')
    if price > upper:
        # sell
        # print('Above bollinger')
        logging.info(f'{symbol}: sell')
        return -1
    elif price < lower:
        # buy
        # print('Below bollinger')
        logging.info(f'{symbol}: buy')
        return 1
    elif price > lowSafe and price < upSafe and short_-long_ < 0:
        # sell
        # print('MA reasons')
        logging.info(f'{symbol}: sell')
        return -1
    elif price > lowSafe and price < upSafe and short_-long_ > 0:
        # buy
        # print('MA reasons')
        logging.info(f'{symbol}: buy')
        return 1
    else:
        # do nothing
        logging.info(f'{symbol}: do nothing')
        return 0


if __name__ == '__main__':
    print(bollingerMA_API(api, 'SNAP'))
    # temp = api.get_barset('SNAP', '1D', limit=1000)
    print(get_bars_list('AAPL', 1)['close'].mean())
