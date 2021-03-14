# Self-made modules
from emailHelper import Emailer
from mlanalysis import MLAnalysis

from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import logging
import os

class Asset(object):
    def __init__(self, api, symbol, buySell):
        self.symbol = symbol
        self.buySell = buySell

        if api == 'own':
            load_dotenv()

            APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
            APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
            APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

            self.api = tradeapi.REST()
        else:
            self.api = api


class Bot(object):
    '''
    Class object that will ultimately run the logic and administrative 
    capacities necessary to run the algorithmic trading bot.

    Will contain within it: a portfolio that will be updated as trades are
    made, the various assets that are being traded, an email handler that
    will email us the results of the bot on a given time delay.

    The class DOES NOT INCLUDE the strategy that is being used. This is 
    being held in python modules that can't be found
    in the github repo due to not wanting to publicly release it.
    '''

    def __init__(self, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(name)s: %(message)s')

        load_dotenv()

        APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
        APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
        APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

        self.api = tradeapi.REST()

    def getHistoricalData(self, symbol, timeframe, startDate, endDate):
        pass

    def getCurrentPrice(self, symbol):
        bars = self.api.get_barset(symbol, '1D', limit=1)
        logging.debug('Last closing price for {} stock: ${}'.format(symbol, 
                                                    bars[symbol][-1].c))
        return bars

if __name__ == '__main__':
    bot = Bot(debug=True)
    print(bot.getCurrentPrice('SNAP')['SNAP'][-1].c)

    # print(api.get_barset('AAPL', 'day', limit=5))
    # assetList = bot.api.list_assets()
    # print(assetList[-1])
    # active = 0
    # for asset in assetList:
    #     if asset.status == 'active' and asset.fractionable:
    #         active += 1
    # print(active)

    # # Check if the market is open now.
    # clock = api.get_clock()
    # print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # # Check when the market was open on Dec. 1, 2018
    # date = '2021-3-11'
    # calendar = api.get_calendar(start=date, end=date)[0]
    # print('The market opened at {} and closed at {} on {}.'.format(
    #     calendar.open,
    #     calendar.close,
    #     date
    # ))

    # print(api.get_bars("AAPL", TimeFrame.Day, "2021-01-01", "2021-01-03", limit=10, adjustment='raw').df)
