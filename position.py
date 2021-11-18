from datetime import datetime
from data_sources.data_reader import DataReader


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self.prices = None
        self.prices_cad = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def get_prices(self, start_date: datetime = None, end_date: datetime = None):
        if self.prices is None:
            prices = self.datareader.read_prices(ticker=self.ticker).astype(float)
            self.prices = prices.loc[end_date: start_date].sort_index()
        return self.prices

    def get_prices_cad(self, start_date: datetime = None, end_date: datetime = None):
        prices = self.get_prices(start_date=start_date, end_date=end_date)

        if self.prices_cad is None and self.currency != 'CAD':
            fx = self.datareader.read_fx(currency=self.currency).loc[end_date: start_date]
            self.prices_cad = (prices * fx).dropna().sort_index()
        else:
            self.prices_cad = prices
        return self.prices_cad
