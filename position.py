from datetime import datetime

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

    def daily_price_diff(self, date: datetime = None) -> pd.Series:
        """
        gives position price difference from last close to date param
        :param date: datetime of date of price difference
        :return: pd.Series of the price difference for given date
        """
        if date is None:
            date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = date - BDay(4)
        dates = dates_utils.get_market_days(start=start_date, end=date)[-2:]
        pnl = self.get_prices().loc[dates].diff().dropna()
        return pnl
