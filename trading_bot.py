import yaml
from config_loader import load_config
from alpaca_client import AlpacaClient
from strategy import BollingerStrategy
from backtester import Backtester

def main():
    # Load configuration
    config = load_config('config.yaml')

    # Initialize Alpaca API client
    client = AlpacaClient(config['api_key'], config['api_secret'])

    # Check if trading is available today
    if not client.is_trading_day():
        print("Trading is not available today.")
        return

    # Fetch current portfolio
    portfolio = client.get_portfolio()

    # Initialize Bollinger Strategy
    strategy = BollingerStrategy(client)

    # Execute strategy
    strategy.execute(portfolio)

    # Backtesting (optional, can be commented out if not needed)
    backtester = Backtester(client, BollingerStrategy, '2021-01-01T00:00:00Z', '2021-12-31T23:59:59Z')
    backtester.run_backtest()

if __name__ == '__main__':
    main()