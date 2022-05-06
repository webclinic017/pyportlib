from abc import abstractmethod
from datetime import datetime
import pandas as pd

from ..utils import files_utils, dates_utils


class BaseDataConnection:
    _DATA_DIRECTORY = files_utils.get_data_dir()
    _STATEMENT_DIRECTORY = files_utils.get_statements_data_dir()
    _PRICES_DIRECTORY = files_utils.get_price_data_dir()
    _FX_DIRECTORY = files_utils.get_fx_data_dir()

    @property
    def data_dir(self):
        return self._DATA_DIRECTORY

    @property
    def statement_dir(self):
        return self._STATEMENT_DIRECTORY

    @property
    def prices_dir(self):
        return self._PRICES_DIRECTORY

    @property
    def fx_dir(self):
        return self._FX_DIRECTORY

    @abstractmethod
    @property
    def file_prefix(self):
        raise NotImplementedError()

    @abstractmethod
    def get_prices(self, ticker: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_fx(self, currency_pair: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_balance_sheet(self, ticker: str):
        raise NotImplementedError()

    @abstractmethod
    def get_cash_flow(self, ticker: str):
        raise NotImplementedError()

    @abstractmethod
    def get_income_statement(self, ticker: str):
        raise NotImplementedError()

    @abstractmethod
    def get_dividends(self, ticker: str, start_date=None, end_date=None):
        raise NotImplementedError()

    @abstractmethod
    def get_splits(self, ticker: str):
        raise NotImplementedError()

    @staticmethod
    def _make_ptf_currency_df() -> pd.DataFrame:
        """
        Portfolio currency is 1
        :return:
        """
        end = dates_utils.last_bday()
        dates = pd.date_range(start=datetime(2000, 1, 1), end=end)
        data = [1 for _ in range(len(dates))]
        return pd.DataFrame(data=data, index=pd.Index(name='Date', data=dates), columns=['Close'])

    @abstractmethod
    @staticmethod
    def _convert_ticker(ticker: str) -> str:
        raise NotImplementedError()