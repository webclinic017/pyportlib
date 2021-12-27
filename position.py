from datetime import datetime
from typing import Union, List

from pandas._libs.tslibs.offsets import BDay
from data_sources.data_reader import DataReader
import pandas as pd

from utils import dates_utils


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self._prices = pd.Series()
        self._quantities = pd.Series()
        self._load_prices()

    def __repr__(self):
        return f"{self.ticker}"

    def _load_prices(self):
        self._prices = self.datareader.read_prices(ticker=self.ticker).astype(float).sort_index()

    def get_prices(self):
        return self._prices

    def set_prices(self, prices: pd.Series) -> None:
        self._prices = prices

    def get_quantities(self) -> pd.Series:
        return self._quantities

    def set_quantities(self, quantities: pd.Series) -> None:
        self._quantities = quantities

    def daily_unrealized_pnl(self, start_date: datetime = None, end_date: datetime = None) -> pd.Series:
        if end_date is None:
            end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date is None:
            start_date = end_date

        search_date = start_date - BDay(4)
        try:
            diff = self.get_prices().loc[search_date:end_date].diff().dropna()
        except KeyError:
            raise KeyError("pnl error")

        pnl = diff.multiply(self.get_quantities().loc[search_date:end_date]).dropna().loc[start_date:end_date]

        return pnl
