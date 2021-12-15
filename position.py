from datetime import datetime
from data_sources.data_reader import DataReader
import pandas as pd


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self.prices = pd.Series()
        self.prices_cad = pd.Series()
        self.quantities = pd.Series()

    def __repr__(self):
        return f"{self.ticker}"

    def get_prices(self, start_date: datetime = None, end_date: datetime = None, reload: bool = False):
        if self.prices.empty or reload:
            prices = self.datareader.read_prices(ticker=self.ticker).astype(float)
            self.prices = prices.loc[end_date: start_date].sort_index()
        return self.prices

    def get_prices_cad(self, start_date: datetime = None, end_date: datetime = None, reload: bool = False):
        prices = self.get_prices(start_date=start_date, end_date=end_date, reload=reload)
        if (self.prices_cad.empty or reload) and self.currency != 'CAD':
            fx = self.datareader.read_fx(currency=self.currency).loc[end_date: start_date]
            self.prices_cad = (prices * fx).dropna().sort_index()
        else:
            self.prices_cad = prices
        return self.prices_cad

    def set_quantities(self, quantities):
        self.quantities = quantities
