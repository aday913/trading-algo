# from emailHelper import Emailer
# from mlanalysis import MLAnalysis

import alpaca_trade_api as tradeapi
import os

from dotenv import load_dotenv

load_dotenv()

APCA_API_SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
APCA_API_KEY_ID = os.getenv('APCA_API_KEY_ID')
APCA_API_BASE_URL = os.getenv('APCA_API_BASE_URL')

api = tradeapi.REST()

# Check if the market is open now.
clock = api.get_clock()
print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

# Check when the market was open on Dec. 1, 2018
date = '2021-3-11'
calendar = api.get_calendar(start=date, end=date)[0]
print('The market opened at {} and closed at {} on {}.'.format(
    calendar.open,
    calendar.close,
    date
))