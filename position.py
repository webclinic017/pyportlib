from datetime import datetime
from data_sources.data_reader import DataReader
import pandas as pd


class Position(object):

    def __init__(self, ticker: str, currency: str, ptf_currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self.prices = pd.Series()
        self.quantities = pd.Series()
        self.pair = f"{currency}{ptf_currency}"

        self._load_prices()

    def __repr__(self):
        return f"{self.ticker}"

    def _load_prices(self):
        self.prices = self.datareader.read_prices(ticker=self.ticker).astype(float).sort_index()

    def get_prices(self):  # FIXME ptf should convert the fx??
        return self.prices

    def set_prices(self, prices: pd.Series):
        self.prices = prices

    def set_quantities(self, quantities):
        self.quantities = quantities
