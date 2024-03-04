import datetime
import os

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

def main(api_key, secret):
    print('In main function, trying to establish client...')
    client = StockHistoricalDataClient(
        api_key=api_key, 
        secret_key=secret, 
    )
    
    print('Setting request parameters')
    request_params = StockBarsRequest(
        symbol_or_symbols=["GOOG", "TSLA"],
        timeframe=TimeFrame.Hour,
        start=datetime.datetime(2022, 9, 1),
        end=datetime.datetime(2022, 9, 14)
    )

    bars = client.get_stock_bars(request_params=request_params)

    print(bars.df)

if __name__ == "__main__":
    load_dotenv()

    api_key = os.environ.get("APCA_API_KEY_ID")
    secret = os.environ.get("APCA_API_SECRET_KEY")

    main(api_key=api_key, secret=secret)
