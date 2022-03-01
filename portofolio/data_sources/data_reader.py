from ..utils import logger, files_utils, config_utils
# from old.alphavantage_connection import AlphaVantageConnection
# from old.simfin_connection import SimFinConnection
from ..data_sources.yahoo_connection import YahooConnection
from ..helpers.transaction_manager import TransactionManager
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
        # if prices_data_source == 'AlphaVantage':
        #     market_data = AlphaVantageConnection()
        # elif prices_data_source == 'SimFin':
        #     market_data = SimFinConnection()
        if prices_data_source == 'Yahoo':
            market_data = YahooConnection()
        else:
            logger.logging.error(f'prices datasource: {prices_data_source} not valid')
            return None
        # data source for statments
        # if statements_data_source == 'AlphaVantage':
        #     statements = AlphaVantageConnection()
        # elif statements_data_source == 'SimFin':
        #     statements = SimFinConnection()
        if prices_data_source == 'Yahoo':
            statements = YahooConnection()
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
            return df['Close']
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
            return df['Close']
        else:
            logger.logging.info(f'no fx data to read for {currency_pair}, now fetching new data from api')
            self.update_fx(currency_pair=currency_pair)
            return self.read_fx(currency_pair)

    def read_fundamentals(self, ticker: str, statement_type: str):
        implemented = {'balance_sheet', 'cash_flow', 'income_statement'}
        if statement_type not in implemented:
            raise ValueError(f'enter valid statement type: {implemented}')
        directory = self._market_data_source.STATEMENT_DIRECTORY
        filename = f"{self._market_data_source.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_{statement_type}.csv"

        if files_utils.check_file(directory=directory, file=filename):
            if statement_type in {"balance_sheet", "cash_flow", "income_statement"}:
                index = "Breakdown"
            else:
                index = 'no index'
            df = pd.read_csv(f"{directory}/{filename}").set_index(index)
            return df

        else:
            logger.logging.info(f'no {statement_type} data to read for {ticker}, now fetching new data from api')
            self.update_statement(ticker=ticker, statement_type=statement_type)
            return self.read_fundamentals(ticker=ticker, statement_type=statement_type)

    def read_dividends(self, ticker: str):
        directory = self._market_data_source.STATEMENT_DIRECTORY
        filename = f"{self._market_data_source.FILE_PREFIX}_{ticker}_dividends.csv"

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

    def last_data_point(self, account: str, ptf_currency: str = 'CAD'):
        last_data = self.read_fx(f'{ptf_currency}{ptf_currency}').sort_index().index[-1]
        last_trade = TransactionManager(account=account).get_transactions().index.max()
        return max(last_data, last_trade)
