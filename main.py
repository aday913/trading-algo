# Self-made modules
from emailHelper import Emailer
from mlanalysis import MLAnalysis
from strategies import bollingerMA_Backtest

from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import logging
import os

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

    def __init__(self, debug=False, strategy):
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

        self.interestedStocks = {}

        self.strategy = strategy

        self.testTrades = {'Buy' : [],
                            'Sell' : [],
                            'Nothing' : []}

        self.emailer = Emailer()

        self.tradedToday = False

        self.maxHold = 150

    def getCurrentAccount(self):
        self.api.get_account()

    def getTradableStocks(self):
        '''
        Gets all of the available stocks to trade and then filters them
        to assets that are active, fractionable, and less than $50 a share

        These assets are then saved in the object's "interestedStocks" dict
        '''
        initial = self.api.list_assets()
        cycle = 0
        for asset in initial:
            logging.debug('Grabbing {} of {} assets...'.format(cycle, 
                                                        len(initial)))
            if asset.status == 'active' and asset.fractionable:
                temp = self.api.get_barset(asset.symbol, '1D', limit=300)
                if temp[asset.symbol][-1].c < 50:
                    prices = []
                    if len(temp[asset.symbol]) == 300:
                        for i in temp[asset.symbol]:
                            prices.append(i.c)
                            self.interestedStocks[asset.symbol] = prices
                    else:
                        self.interestedStocks[asset.symbol] = None
            cycle += 1

    def getCurrentPrice(self, symbol):
        '''
        Grabs the latest closing price of a asset given its symbol

        Returns both the closing price and the overall price data at that
        timepoint
        '''
        bars = self.api.get_barset(symbol, '1Min', limit=1)
        logging.debug('Last closing price for {} stock: ${}'.format(symbol, 
                                                    bars[symbol][-1].c))
        closing = bars[symbol][-1].c
        return closing, bars

    def runTest(self):
        '''
        For testing purposes, the function will first find out which assets 
        we are interested in (see self.getTradableStocks()), then for every
        stock that comes back we use the given strategy to determine
        whether or not we buy or sell the stock that day
        '''
        # if self.api.get_clock().is_open and not self.tradedToday:
        if not self.tradedToday:
            self.getTradableStocks()
            for stock in self.interestedStocks:
                if self.interestedStocks[stock] != None:
                    buySell = self.strategy(stock, self.interestedStocks[stock])
                    if buySell == 1:
                        self.testTrades['Buy'].append(stock)
                    elif buySell == -1:
                        self.testTrades['Sell'].append(stock)
                    else:
                        self.testTrades['Nothing'].append(stock)
            self.tradedToday = True
            logging.debug('# of stocks to buy: {}'.format(
                                                len(self.testTrades['Buy'])
            ))
            logging.debug('# of stocks to sell: {}'.format(
                                                len(self.testTrades['Sell'])
            ))
            message = '''Here is what would have been traded today:
            
            The following would have been bought:\n
            '''
            for i in self.testTrades['Buy']:
                message = message + '  ' + str(i) + '\n'
            message = message + '''
            The following would have been sold:\n
            '''
            for i in self.testTrades['Sell']:
                message = message + '  ' + str(i) + '\n'
            self.emailer.sendMessage(message, subject='Test Trades!')
    
    def rebalance(self):
        '''
        Method meant to rebalance our holds on a daily basis to ensure optimal
        algorithmic trading
        '''
        pass
    
    def run(self):
        '''

        '''
        pass

    def order(self, symbol, shares, buySell):
        '''
        Method used to make the ordering process smoother
        '''
        self.api.submit_order(symbol=symbol,
                            side=buySell,
                            type='market',
                            qty=shares,
                            time_in_force='day'
                            )
    
    def dailyLoop(self):
        '''

        '''
        if self.api.get_clock().is_open and not self.tradedToday:
            pass


if __name__ == '__main__':
    bot = Bot(debug=True, strategy=bollingerMA_Backtest)
    bot.getCurrentPrice('SNAP')
    bot.runTest()

    # # Check if the market is open now.
    # clock = api.get_clock()
    # print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # print(api.get_bars("AAPL", TimeFrame.Day, "2021-01-01", "2021-01-03", limit=10, adjustment='raw').df)
