from config import config_utils
from data_sources.alphavantage_connection import AlphaVantageConnection
from data_sources.simfin_connection import SimFinConnection
from data_sources.yfinance_connection import YFinanceConnection
from transaction_manager import TransactionManager
from utils import logger, files_utils
import pandas as pd


class DataReader(object):
    NAME = 'Data Reader'

    def __init__(self):
        _prices_data_source = None
        _statements_data_source = None
        self._set_sources()

    def __repr__(self):
        return self.NAME

    def _set_sources(self) -> None:
        prices_data_source = config_utils.fetch_data_sources('market_data')
        statements_data_source = config_utils.fetch_data_sources('statements')
        # data_source for prices and fx
        if prices_data_source == 'AlphaVantage':
            market_data = AlphaVantageConnection()
        elif prices_data_source == 'SimFin':
            market_data = SimFinConnection()
        elif prices_data_source == 'YFinance':
            market_data = YFinanceConnection()
        else:
            logger.logging.error(f'prices datasource: {prices_data_source} not valid')
            return None
        # data source for statments
        if statements_data_source == 'AlphaVantage':
            statements = AlphaVantageConnection()
        elif statements_data_source == 'SimFin':
            statements = SimFinConnection()
        elif prices_data_source == 'YFinance':
            statements = YFinanceConnection()
        else:
            logger.logging.error(f'statements datasource: {statements_data_source} not valid')
            return None
        self._market_data_source = market_data
        self._statements_data_source = statements

    def read_prices(self, ticker):
        directory = self._market_data_source.PRICES_DIRECTORY
        filename = f"{self._market_data_source.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_prices.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index)
            return df[['Close']]
        else:
            logger.logging.info(f'no price data to read for {ticker}, now fetching new data from api')
            self.update_prices(ticker=ticker)
            return self.read_prices(ticker)

    def read_fx(self, currency_pair: str):
        directory = self._market_data_source.FX_DIRECTORY
        filename = f"{self._market_data_source.FILE_PREFIX}_{currency_pair}_fx.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index)
            return df[['Close']]
        else:
            logger.logging.info(f'no fx data to read for {currency_pair}, now fetching new data from api')
            self.update_fx(currency_pair=currency_pair)
            return self.read_fx(currency_pair)

    def update_prices(self, ticker: str):
        self._market_data_source.get_prices(ticker=ticker)

    def update_fx(self, currency_pair: str):
        self._market_data_source.get_fx(currency_pair=currency_pair)

    def last_data_point(self, account: str):
        last_data = self.read_fx('CADCAD').sort_index().index[-1]
        last_trade = TransactionManager(account=account).transactions.index.max()
        return max(last_data, last_trade)