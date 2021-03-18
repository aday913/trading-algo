from main import Asset
from strategies import bollingerMA_API

from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv

import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import logging
import os

class Portfolio(object):
    '''
    Portfolio object that will keep track of the various assets that
    we buy/sell, as well as track the equity available
    '''
    def __init__(self, api, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(name)s: %(message)s')
        
        if api == 'own':
            load_dotenv()

            APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
            APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
            APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

            self.api = tradeapi.REST()
        else:
            self.api = api

class Backtest(object):
    def __init__(self, api, strategy, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(name)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(name)s: %(message)s')

        if api == 'own':
            load_dotenv()

            APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
            APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
            APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

            self.api = tradeapi.REST()
        else:
            self.api = api

        self.testableSymbols = self.getHistoricalData()
        self.portfolio = Portfolio()

    def getHistoricalData(self):
        initial = self.api.list_assets()
        backtestable = {}
        i = 0
        for asset in initial:
            logging.debug('Grabbing {} of {} assets...'.format(i, len(initial)))
            if asset.status == 'active' and asset.fractionable:
                temp = self.api.get_barset(asset.symbol, '1D', limit=1000)
                prices = []
                for i in temp[asset.symbol]:
                    prices.append(temp[asset.symbol].)
                if len(temp[asset.symbol]) == 1000:
                    backtestable[asset.symbol] = prices
            i += 1
        return backtestable
        

if __name__ == '__main__':
    test = Backtest(api='own', strategy=None, debug=True)