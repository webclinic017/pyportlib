from datetime import datetime
from .base_data_connection import BaseDataConnection
from ..utils import logger, files_utils, config_utils
from ..data_sources.yahoo_connection import YahooConnection
from ..services.transaction_manager import TransactionManager
import pandas as pd


class DataReader:
    NAME = 'Data Reader'

    def __init__(self):
        _prices_data_source: BaseDataConnection
        _statements_data_source: BaseDataConnection
        self._set_sources()

    def __repr__(self):
        return self.NAME

    def _set_sources(self) -> None:
        prices_data_source = config_utils.fetch_data_sources('market_data')
        statements_data_source = config_utils.fetch_data_sources('statements')
        if prices_data_source == 'Yahoo':
            market_data = YahooConnection()
        else:
            logger.logging.error(f'prices datasource: {prices_data_source} not valid')
            return None

        if prices_data_source == 'Yahoo':
            statements = YahooConnection()
        else:
            logger.logging.error(f'statements datasource: {statements_data_source} not valid')
            return None
        self._market_data_source = market_data
        self._statements_data_source = statements

    def read_prices(self, ticker: str) -> pd.Series:
        """
        Read prices saved locally in client data folder.
        If no .csv found, prices will be fetched
        :param ticker: stock ticker
        :return:
        """
        directory = self._market_data_source.prices_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker.replace('.TO', '_TO')}_prices.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index)
            return df['Close']
        else:
            logger.logging.info(f'no price data to read for {ticker}, now fetching new data from api')
            self.update_prices(ticker=ticker)
            return self.read_prices(ticker)

    def read_fx(self, currency_pair: str) -> pd.Series:
        """
        Read fx rates saved locally in client data folder.
        If no .csv found, rates will be fetched
        :param currency_pair: fx pair ex. USDCAD or CADUSD
        :return:
        """
        directory = self._market_data_source.fx_dir
        filename = f"{self._market_data_source.file_prefix}_{currency_pair}_fx.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index)
            return df['Close']
        else:
            logger.logging.info(f'no fx data to read for {currency_pair}, now fetching new data from api')
            self.update_fx(currency_pair=currency_pair)
            return self.read_fx(currency_pair)

    def read_fundamentals(self, ticker: str, statement_type: str) -> pd.DataFrame:
        """
        Read statements saved locally in client data folder.
        If no .csv found, statements will be fetched
        :param ticker: stocke ticker to read fundamentals data from
        :param statement_type: choose from ('balance_sheet', 'cashflow', 'income_statement')
        :return: dataframe with statement data
        """
        implemented = {'balance_sheet', 'cash_flow', 'income_statement'}
        if statement_type not in implemented:
            raise ValueError(f'enter valid statement type: {implemented}')
        directory = self._market_data_source.statement_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker.replace('.TO', '_TO')}_{statement_type}.csv"

        if files_utils.check_file(directory=directory, file=filename):
            df = pd.read_csv(f"{directory}/{filename}").set_index("Breakdown")
            return df
        else:
            logger.logging.info(f'no {statement_type} data to read for {ticker}, now fetching new data from api')
            self.update_statement(ticker=ticker, statement_type=statement_type)
            return self.read_fundamentals(ticker=ticker, statement_type=statement_type)

    def read_dividends(self, ticker: str):
        """
        Read dividends data saved locally in client data folder.
        If no .csv found, dividends data will be fetched
        :param ticker:
        :return:
        """
        directory = self._market_data_source.statement_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker}_dividends.csv"

        if files_utils.check_file(directory=directory, file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('date')
            df.index = pd.to_datetime(df.index)
            return df['dividend']
        else:
            logger.logging.info(f'no dividend data to read for {ticker}, now fetching new data from api')
            self.update_dividends(ticker=ticker)
            return self.read_dividends(ticker)

    def update_prices(self, ticker: str):
        self._market_data_source.get_prices(ticker=ticker)

    def update_fx(self, currency_pair: str):
        self._market_data_source.get_fx(currency_pair=currency_pair)

    def update_statement(self, ticker: str, statement_type: str):
        if statement_type == 'balance_sheet':
            self._statements_data_source.get_balance_sheet(ticker)
        elif statement_type == 'cash_flow':
            self._statements_data_source.get_cash_flow(ticker)
        elif statement_type == 'income_statement':
            self._statements_data_source.get_cash_flow(ticker)

        elif statement_type == 'all':
            self._statements_data_source.get_balance_sheet(ticker)
            self._statements_data_source.get_cash_flow(ticker)
            self._statements_data_source.get_income_statement(ticker)
        else:
            raise NotImplementedError({statement_type})

    def update_dividends(self, ticker: str):
        self._market_data_source.get_dividends(ticker=ticker)

    def get_splits(self, ticker: str):
        """
        Read stock splits data saved locally in client data folder.
        If no .csv found, splits data will be fetched
        :param ticker:
        :return:
        """
        return self._market_data_source.get_splits(ticker=ticker)

    def last_data_point(self, account: str, ptf_currency: str = 'CAD') -> datetime:
        """
        Find last data point fetched in locally saved files.
        :param account: Portofolio account name
        :param ptf_currency: portfolio currency
        :return:
        """
        last_data = self.read_fx(f'{ptf_currency}{ptf_currency}').sort_index().index[-1]
        last_trade = TransactionManager(account=account).transactions.index.max()
        return max(last_data, last_trade)
