# Self-made modules:
from emailHelper import Emailer
from mlanalysis import MLAnalysis
from strategies import bollingerMA_API, get_bars_list
# from strategies import bollingerMA_Backtest

# Third-party modules:
from alpaca_trade_api.rest import TimeFrame
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd

# Python standard modules:
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

    def __init__(self, strategy, debug=False):
        if debug:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(name)s %(message)s')
        else:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(name)s %(message)s')

        load_dotenv()

        APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
        APCA_API_KEY_ID     = os.getenv('APCA_API_KEY_ID')
        APCA_API_BASE_URL   = os.getenv('APCA_API_BASE_URL')

        self.api = tradeapi.REST()

        self.interestedStocks = {}

        self.strategy = strategy

        self.daily_orders = {'Buy' : [],
                            'Sell' : [],
                            'Nothing' : []}

        self.emailer = Emailer()

        self.maxHold = 150

        self.account = self.getCurrentAccount()

    def getAccountStatus(self):
        if self.account != None:
            return self.account.status()

    def getCurrentAccount(self):
        return self.api.get_account()

    def getTradableStocks(self):
        '''
        Gets all of the available stocks to trade and then filters them
        to assets that are active, fractionable, and less than $50 a share

        These assets are then saved in the object's "interestedStocks" dict
        '''
        now = datetime.datetime.now()
        now = now - datetime.timedelta(days=1)
        
        initial = self.api.list_assets()
        cycle = 0
        logging.info('Grabbing tradable assets using api...')
        for asset in initial:
            logging.debug('Grabbing {} of {} assets...'.format(cycle, 
                                                        len(initial)))

            # Check if the asset is active and fractionable
            if asset.status == 'active' and asset.fractionable:
                temp = self.api.get_bars(
                        asset.symbol, 
                        TimeFrame.Day,
                        start=(
                            now-datetime.timedelta(days=5)
                            ).strftime('%Y-%m-%d'),
                        end=now.strftime('%Y-%m-%d'),
                        adjustment='raw',
                    ).df

                # Check if the newest price is less than $50
                if temp.shape[0] > 0:
                    if temp['close'].mean() < 50:
                        self.interestedStocks[asset.symbol] = {}

            if len(self.interestedStocks.keys()) > 100:
                break
            cycle += 1
        logging.info('Done grabbing tradable assets')

    def getCurrentPrice(self, symbol):
        '''
        Grabs the latest closing price of a asset given its symbol

        Returns both the closing price and the overall price data at that
        timepoint
        '''
        now = datetime.datetime.now()
        now = now - datetime.timedelta(days=1)
        
        bars = self.api.get_bars(
            symbol, 
            TimeFrame.Day, 
            start=(
                now - datetime.timedelta(days=1)
                ).strftime(
                    '%Y-%m-%d'
                    ),
            end=now.strftime('%Y-%m-%d'), 
            adjustment='raw',
            ).df
        closing = bars['close'].mean()
        logging.info('Last closing price for {} stock: ${}'.format(symbol, 
                                                    closing))
        return closing, bars

    def runTest(self):
        '''
        For testing purposes, the function will first find out which assets 
        we are interested in (see self.getTradableStocks()), then for every
        stock that comes back we use the given strategy to determine
        whether or not we buy or sell the stock that day
        '''
        # if self.api.get_clock().is_open and not self.tradedToday:
        self.getTradableStocks()
        for stock in self.interestedStocks:
            buySell = self.strategy(self.api, stock)
            if buySell == 1:
                self.daily_orders['Buy'].append(stock)
            elif buySell == -1:
                self.daily_orders['Sell'].append(stock)
            else:
                self.daily_orders['Nothing'].append(stock)
        logging.info('# of stocks to buy: {}'.format(
                                            len(self.daily_orders['Buy'])
        ))
        logging.info('# of stocks to sell: {}'.format(
                                            len(self.daily_orders['Sell'])
        ))
        message = '''Here is what would have been traded today:
        
        The following would have been bought:\n
        '''
        for i in self.daily_orders['Buy']:
            message = message + '  ' + str(i) + '\n'
        message = message + '''
        The following would have been sold:\n
        '''
        for i in self.daily_orders['Sell']:
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
    bot = Bot(debug=True, strategy=bollingerMA_API)
    # bot.getCurrentPrice('SNAP')
    bot.runTest()

    # # Check if the market is open now.
    # clock = api.get_clock()
    # print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

    # print(api.get_bars("AAPL", TimeFrame.Day, "2021-01-01", "2021-01-03", limit=10, adjustment='raw').df)
