from datetime import datetime
from data_sources.data_reader import DataReader


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self.prices = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def get_prices(self, start_date: datetime = None, end_date: datetime = None):
        if self.prices is None:
            prices = self.datareader.read_prices(ticker=self.ticker).astype(float)
            self.prices = prices.loc[end_date: start_date]
        return self.prices
