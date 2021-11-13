from datetime import datetime
import pandas as pd
import requests

from data_sources.av_request_manager import request_limit
from utils.config_utils import fetch_key
from utils.files_utils import check_file


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

    def get_prices(self,
                   ticker: str,
                   start: datetime,
                   end: datetime,
                   read: bool = True) -> pd.DataFrame:
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TRT', '')}_prices.csv"
        directory = self.PRICES_DIRECTORY
        if read:
            if check_file(directory=directory, file=filename):
                df = pd.read_csv(f"{directory}/{filename}")
                print(f"{ticker}: last date retrieved: {df.Date.max()}")
                return df.loc[(df.Date >= start) & (df.Date <= end)].set_index('Date')

        currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
        request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={self.api_key}"

        request = requests.get(request_url)
        request_limit()
        data = request.json()
        metadata = data.get('Meta Data')
        data = data.get('Time Series (Daily)')
        # data = pd.DataFrame.from_dict(data, orient='index')
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if data is None or request.status_code != 200:
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = columns
        df.index.name = 'Date'
        df['Currency'] = currency
        df['Ticker'] = ticker

        df.to_csv(f"{directory}/{filename}")
        return df.loc[(df.index >= start) & (df.index <= end)]

    def get_fx(self,
               currency: str,
               start: datetime,
               end: datetime,
               read: bool = True) -> pd.DataFrame:
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        filename = f"{self.FILE_PREFIX}_{currency}CAD_fx.csv"
        directory = self.FX_DIRECTORY
        if read:
            if check_file(directory=directory, file=filename):
                df = pd.read_csv(f"{directory}/{filename}")
                print(f"{currency}: last date retrieved: {df.Date.max()}")
                return df.loc[(df.Date >= start) & (df.Date <= end)].set_index('Date')
        pair = f"{currency}CAD"
        request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={pair}&outputsize=full&apikey={self.api_key}"

        request = requests.get(request_url)
        request_limit()
        data = request.json()
        metadata = data.get('Meta Data')
        data = data.get('Time Series (Daily)')
        # data = pd.DataFrame.from_dict(data, orient='index')
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if data is None or request.status_code != 200:
            return pd.DataFrame()

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = columns
        df.index.name = 'Date'
        df['Ticker'] = pair

        df.to_csv(f"{directory}/{filename}")
        return df.loc[(df.index >= start) & (df.index <= end)]
