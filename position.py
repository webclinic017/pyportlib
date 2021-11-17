from datetime import datetime
from data_sources.data_source_manager import DataSourceManager
from utils.dates_utils import get_market_days


class Position(object):

    def __init__(self, ticker: str, currency: str, connection: DataSourceManager):
        self.ticker = ticker
        self.currency = currency
        self.connection = connection
        self.prices_local = None
        self.prices_cad = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def load_prices_local(self, read: bool = True):
        if self.prices_local is None or not read:
            self.prices_local = self.connection.prices_local(ticker=self.ticker, read=read).loc[:, ['Close']]
            self.prices_local.loc[:, 'Close'] = self.prices_local.Close.astype(float)

    def load_prices_cad(self, read: bool = True):

        if self.prices_local is None:
            self.load_prices_local(read=read)

        if self.currency == 'CAD':
            self.prices_cad = self.prices_local
        else:
            fx = self.connection.fx(currency=self.currency, read=True).loc[:, ['Close']]
            fx.Close = fx.Close.astype(float)
            if self.prices_cad is None:
                self.prices_cad = self.prices_local * fx.loc[fx.index.isin(self.prices_local.index)]
