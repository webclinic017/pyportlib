from datetime import datetime
from data_sources.data_source_manager import DataSourceManager


class Position(object):

    def __init__(self, ticker: str, currency: str):
        self.ticker = ticker
        self.currency = currency
        self.connection = DataSourceManager()
        self.prices_local = None
        self.prices_cad = None

    def __repr__(self):
        return f"{self.ticker} - Equity"

    def load_prices_local(self,
                          start: datetime = datetime(1990, 1, 1),
                          end: datetime = datetime.today(),
                          read: bool = True):
        if self.prices_local is None:
            self.prices_local = self.connection.prices_local(ticker=self.ticker, start=datetime(1990, 1, 1),
                                                             end=datetime.today(), read=read)[['Close']]
            self.prices_local.Close = self.prices_local.Close.astype(float)
        return self.prices_local.loc[
            (self.prices_local.index >= start.strftime("%Y-%m-%d")) & (
                    self.prices_local.index <= end.strftime("%Y-%m-%d"))]

    def load_prices_cad(self,
                        start: datetime = datetime(1999, 1, 1),
                        end: datetime = datetime.today(),
                        read: bool = True):
        if not read and self.currency != 'CAD':
            self.connection.refresh_fx(self.currency)

        if self.prices_local is None:
            raise AttributeError('load local prices before CAD prices')

        if self.currency != 'CAD':
            fx = self.connection.fx(currency=self.currency, start=start,
                                    end=end, read=True)[['Close']]
            fx.Close = fx.Close.astype(float)
            if self.prices_cad is None:
                self.prices_cad = self.prices_local * fx.loc[fx.index.isin(self.prices_local.index)]
            return self.prices_cad.loc[
                (self.prices_cad.index >= start.strftime("%Y-%m-%d")) & (
                        self.prices_cad.index <= end.strftime("%Y-%m-%d"))]
        else:
            return self.prices_local[
                (self.prices_local.index >= start.strftime("%Y-%m-%d")) & (
                        self.prices_local.index <= end.strftime("%Y-%m-%d"))]
