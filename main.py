import os
import argparse

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv

from trading_algo.backtesting import Backtest

class AlgoManager:
    def __init__(self, api_key_id, api_secret_key, command):
        self.client = TradingClient(
            api_key=api_key_id, 
            secret_key=api_secret_key,
            paper=True
        )
        self.historical_data = StockHistoricalDataClient(
            api_key=api_key_id,
            secret_key=api_secret_key,
        )

        self.command = command

        self.backtest_manager = Backtest()

    def _is_market_open(self):
        clock = self.client.get_clock()
        return clock.is_open

    def execute_trade(self):  # Placeholder, you'll implement your strategy details later
        if self._is_market_open():
            print("Executing trade...")
        else:
            print("Market is currently closed.")

    def run_backtest(self):  # Placeholder, you'll integrate your backtester later
        print("Running backtest...")

if __name__ == '__main__':
    load_dotenv()  # Load environment variables

    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['backtest', 'trade'], help='Command to execute')
    args = parser.parse_args()

    manager = AlgoManager(
        os.getenv('PAPER_APCA_API_KEY_ID'),
        os.getenv('PAPER_APCA_API_SECRET_KEY'),
        args.command
    )

    if args.command == 'backtest':
        manager.run_backtest()
    elif args.command == 'trade':
        manager.execute_trade()

