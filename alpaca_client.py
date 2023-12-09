import alpaca_trade_api as tradeapi
from datetime import datetime
import pytz

class AlpacaClient:
    def __init__(self, api_key, api_secret):
        self.api = tradeapi.REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')

    def is_trading_day(self):
        """Check if today is a trading day."""
        calendar = self.api.get_calendar(start=datetime.now(pytz.UTC), end=datetime.now(pytz.UTC))
        return len(calendar) > 0

    def get_portfolio(self):
        """Fetch the current portfolio."""
        return self.api.list_positions()

    def submit_order(self, symbol, qty, side, type, time_in_force):
        """Submit an order to the Alpaca API."""
        self.api.submit_order(symbol=symbol, qty=qty, side=side, type=type, time_in_force=time_in_force)