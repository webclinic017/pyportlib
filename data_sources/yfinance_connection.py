from datetime import datetime
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yfin
from utils import logger, files_utils, dates_utils


class YFinanceConnection(object):
    STATEMENT_DIRECTORY = 'client_data/data/statements'
    PRICES_DIRECTORY = 'client_data/data/prices'
    FX_DIRECTORY = 'client_data/data/fx'
    FILE_PREFIX = 'yfin'
    NAME = 'YFinance'
    URL = ''
    yfin.pdr_override()

    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.NAME} API Connection"

    def get_prices(self, ticker: str) -> None:
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_prices.csv"
        directory = self.PRICES_DIRECTORY
        ticker = self._convert_ticker(ticker)
        data = pdr.get_data_yahoo(ticker)
        data.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']

        if not files_utils.check_dir(directory):
            files_utils.make_dir(directory)
        data.to_csv(f"{directory}/{filename}")
        logger.logging.info(f"{ticker} loaded from yfinance api")

    def get_fx(self, currency_pair: str) -> None:
        filename = f"{self.FILE_PREFIX}_{currency_pair}_fx.csv"
        directory = self.FX_DIRECTORY

        if currency_pair[:3] == currency_pair[-3:]:
            data = self._make_ptf_currency_df()
        else:
            data = pdr.get_data_yahoo(f'{currency_pair}=X')
            data.columns = ['Open', 'High', 'Low', 'Close', 'AdjClose', 'Volume']

        if not files_utils.check_dir(directory):
            files_utils.make_dir(directory)
        data.to_csv(f"{directory}/{filename}")
        logger.logging.info(f"{currency_pair} loaded from yfinance api")

    @staticmethod
    def _make_ptf_currency_df():
        dates = dates_utils.get_market_days(start=datetime(2000, 1, 1))
        data = [1 for _ in range(len(dates))]
        return pd.DataFrame(data=data, index=pd.Index(name='Date', data=dates), columns=['Close'])

    @staticmethod
    def _convert_ticker(ticker):
        ticker = ticker.replace('.TRT', '.TO')
        ticker = ticker.replace(' ', '')
        return ticker
