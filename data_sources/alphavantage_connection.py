import pandas as pd
import requests
from data_sources.alpha_vantage_request_manager import request_limit_manager
from utils import logger
from config.config_utils import fetch_key


class AlphaVantageConnection(object):
    STATEMENT_DIRECTORY = 'client_data/data/statements'
    PRICES_DIRECTORY = 'client_data/data/prices'
    FX_DIRECTORY = 'client_data/data/fx'
    FILE_PREFIX = 'AV'
    NAME = 'AlphaVantage'
    URL = 'https://www.alphavantage.co/query?'
    MAX_RPM = 5

    def __init__(self):
        self.api_key = fetch_key(self.NAME)
        self.rpm = 0
        self.requests = {}

    def __repr__(self):
        return f"{self.NAME} API Connection"

    def get_prices(self, ticker: str) -> None:

        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TRT', '_TRT')}_prices.csv"
        directory = self.PRICES_DIRECTORY

        currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
        request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={self.api_key}"

        request = requests.get(request_url)

        data = request.json()
        data = data.get('Time Series (Daily)')
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if data is None or request.status_code != 200:
            logger.logging.error(f'request limit reached ({ticker}), trying again')
            request_limit_manager(ticker, restarted=True)
            return self.get_prices(ticker=ticker)

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = columns
        df.index.name = 'Date'
        df['Currency'] = currency
        df['Ticker'] = ticker
        df.to_csv(f"{directory}/{filename}")
        request_limit_manager(ticker)

    def get_fx(self, currency: str) -> None:

        filename = f"{self.FILE_PREFIX}_{currency}CAD_fx.csv"
        directory = self.FX_DIRECTORY

        pair = f"{currency}CAD"
        request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={pair}&outputsize=full&apikey={self.api_key}"

        request = requests.get(request_url)

        data = request.json()
        data = data.get('Time Series (Daily)')
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if data is None or request.status_code != 200:
            logger.logging.error(f'request limit reached ({currency}), trying again')
            request_limit_manager(currency, restarted=True)
            return self.get_fx(currency=currency)

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = columns
        df.index.name = 'Date'
        df['Ticker'] = pair

        df.to_csv(f"{directory}/{filename}")
        request_limit_manager('fx')
