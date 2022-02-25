from datetime import datetime

import pandas as pd
import requests
from ..data_sources.alpha_vantage_request_manager import request_limit_manager
from ..utils import dates_utils, logger, files_utils
from ..utils.config_utils import fetch_key


class AlphaVantageConnection(object):
    STATEMENT_DIRECTORY = 'client_data/data/statements'
    PRICES_DIRECTORY = 'client_data/data/prices'
    FX_DIRECTORY = 'client_data/data/_fx'
    FILE_PREFIX = 'AV'
    NAME = 'AlphaVantage'
    URL = 'https://www.alphavantage.co/query?'

    def __init__(self):
        self.api_key = fetch_key(self.NAME)

    def __repr__(self):
        return f"{self.NAME} API Connection"

    def get_prices(self, ticker: str) -> None:

        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TRT', '_TRT')}_prices.csv"
        directory = self.PRICES_DIRECTORY

        request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={self._convert_ticker(ticker)}&outputsize=full&apikey={self.api_key}"

        request = requests.get(request_url)

        data = request.json()
        data = data.get('Time Series (Daily)')
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        if data is None or request.status_code != 200:
            logger.logging.info(f'request limit reached ({ticker}), trying again')
            request_limit_manager(ticker, restarted=True)
            return self.get_prices(ticker=ticker)

        df = pd.DataFrame.from_dict(data, orient='index')
        df.columns = columns
        df.index.name = 'Date'
        if not files_utils.check_dir(directory):
            files_utils.make_dir(directory)
        df.to_csv(f"{directory}/{filename}")
        request_limit_manager(ticker)

    def get_fx(self, currency_pair: str) -> None:

        filename = f"{self.FILE_PREFIX}_{currency_pair}_fx.csv"
        directory = self.FX_DIRECTORY

        if currency_pair[:3] == currency_pair[-3:]:
            data = self._make_ptf_currency_df()
        else:
            request_url = f"{self.URL}function=TIME_SERIES_DAILY&symbol={currency_pair}&outputsize=full&apikey={self.api_key}"

            request = requests.get(request_url)

            data = request.json()
            data = data.get('Time Series (Daily)')
            columns = ['Open', 'High', 'Low', 'Close', 'Volume']

            if data is None or request.status_code != 200:
                logger.logging.error(f'request limit reached ({currency_pair}), trying again')
                request_limit_manager(currency_pair, restarted=True)
                return self.get_fx(currency_pair=currency_pair)

            data = pd.DataFrame.from_dict(data, orient='index')
            data.columns = columns
            data.index.name = 'Date'
        if not files_utils.check_dir(directory):
            files_utils.make_dir(directory)
        data.to_csv(f"{directory}/{filename}")
        request_limit_manager('_fx')

    @staticmethod
    def _make_ptf_currency_df():
        dates = dates_utils.get_market_days(start=datetime(2000, 1, 1))
        data = [1 for _ in range(len(dates))]
        return pd.DataFrame(data=data, index=pd.Index(name='Date', data=dates), columns=['Close'])

    @staticmethod
    def _convert_ticker(ticker):
        ticker = ticker.replace('.TO', '.TRT')
        ticker = ticker.replace(' ', '')
        return ticker
