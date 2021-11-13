from datetime import datetime
from data_sources.data_source_manager import DataSourceManager


class Position(object):

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.connection = DataSourceManager()
        self.prices = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def fetch_prices(self,
                     start: datetime = datetime(1990, 1, 1),
                     end: datetime = datetime.today(),
                     read: bool = True):
        if self.prices is None:
            self.prices = self.connection.prices(ticker=self.ticker, start=datetime(1990, 1, 1), end=datetime.today(), read=read)

        return self.prices.loc[(self.prices.index >= start.strftime("%Y-%m-%d")) & (self.prices.index <= end.strftime("%Y-%m-%d"))]
