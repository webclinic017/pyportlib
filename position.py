from datetime import datetime
from data_sources.data_reader import DataReader
from utils import dates_utils


class Position(object):

    def __init__(self, ticker: str, currency: str, datareader: DataReader):
        self.ticker = ticker
        self.currency = currency
        self.datareader = datareader
        self.prices = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def get_prices(self, start_date: datetime, end_date: datetime = None):
        if self.prices is None:
            self.prices = self.datareader.read_prices(ticker=self.ticker).loc[:, ['Close']].astype(float)
        return self.prices.loc[start_date: end_date]
