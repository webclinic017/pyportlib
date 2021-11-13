from datetime import datetime

from data_sources.alphavantage_connection import AlphaVantageConnection
from data_sources.simfin_connection import SimFinConnection
from utils.config_utils import fetch_data_sources


class DataSourceManager(object):
    _prices_data_source = AlphaVantageConnection()
    _statements_data_source = AlphaVantageConnection()
    NAME = 'Data Source Manager'

    def __init__(self):
        self.set_sources()

    def __repr__(self):
        return self.NAME

    def set_sources(self):
        prices_data_source = fetch_data_sources('prices')
        statements_data_source = fetch_data_sources('statements')
        if prices_data_source == 'AlphaVantage':
            prices = AlphaVantageConnection()
        elif prices_data_source == 'SimFin':
            prices = SimFinConnection()
        else:
            raise ValueError(f'prices datasource: {prices_data_source} not valid')

        if statements_data_source == 'AlphaVantage':
            statements = AlphaVantageConnection()
        elif statements_data_source == 'SimFin':
            statements = SimFinConnection()
        else:
            raise ValueError(f'statements datasource: {statements_data_source} not valid')

        self._prices_data_source = prices
        self._statements_data_source = statements
        return prices, statements

    def prices_local(self,
                     ticker: str,
                     start: datetime,
                     end: datetime,
                     read: bool = True):
        return self._prices_data_source.get_prices(ticker=ticker, start=start, end=end, read=read)

    def fx(self,
           currency: str,
           start: datetime,
           end: datetime,
           read: bool = True):
        return self._prices_data_source.get_fx(currency=currency, start=start, end=end, read=read)

    def statements(self):
        raise NotImplemented
