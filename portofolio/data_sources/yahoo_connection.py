from datetime import datetime
import pandas as pd
from ..utils import logger, files_utils
from pandas_datareader import data as pdr
import yfinance as yfin
import yahoo_fin.stock_info as yf


class YahooConnection(object):
    DATA_DIRECTORY = files_utils.get_data_dir()
    STATEMENT_DIRECTORY = files_utils.get_statements_data_dir()
    PRICES_DIRECTORY = files_utils.get_price_data_dir()
    FX_DIRECTORY = files_utils.get_fx_data_dir()
    FILE_PREFIX = 'yfin'
    NAME = 'Yahoo'
    URL = ''
    yfin.pdr_override()

    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.NAME} API Connection"

    def get_prices(self, ticker: str) -> None:
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_prices.csv"
        directory = self.PRICES_DIRECTORY
        ticker = self._convert_ticker(ticker)
        data = pdr.get_data_yahoo(ticker, progress=False)
        data.columns = [col.replace(' ', '') for col in data.columns]

        data.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} loaded from yfinance api")

    def get_fx(self, currency_pair: str) -> None:
        filename = f"{self.FILE_PREFIX}_{currency_pair}_fx.csv"
        directory = self.FX_DIRECTORY

        if currency_pair[:3] == currency_pair[-3:]:
            data = self._make_ptf_currency_df()
        else:
            data = pdr.get_data_yahoo(f'{currency_pair}=X', progress=False)
            data.columns = [col.replace(' ', '') for col in data.columns]

        data.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{currency_pair} loaded from yfinance api")

    def get_balance_sheet(self, ticker: str):
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_balance_sheet.csv"
        directory = self.STATEMENT_DIRECTORY
        ticker = self._convert_ticker(ticker)
        try:
            bs = yf.get_balance_sheet(ticker)
        except KeyError:
            bs = pd.DataFrame()
        bs.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} balance_sheet loaded from yfinance api")

    def get_cash_flow(self, ticker: str):
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_cash_flow.csv"
        directory = self.STATEMENT_DIRECTORY
        ticker = self._convert_ticker(ticker)

        try:
            cf = yf.get_cash_flow(ticker)
        except KeyError or TypeError:
            cf = pd.DataFrame()
        cf.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} cash flow loaded from yfinance api")

    def get_income_statement(self, ticker: str):
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_income_statement.csv"
        directory = self.STATEMENT_DIRECTORY
        ticker = self._convert_ticker(ticker)

        try:
            bs = yf.get_cash_flow(ticker)
        except KeyError:
            bs = pd.DataFrame()
        bs.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} income statement loaded from yfinance api")

    def get_dividends(self, ticker: str, start_date=None, end_date=None):
        filename = f"{self.FILE_PREFIX}_{ticker.replace('.TO', '_TO')}_dividends.csv"
        directory = self.STATEMENT_DIRECTORY
        ticker = self._convert_ticker(ticker)
        divs = yf.get_dividends(ticker, start_date=start_date, end_date=end_date, index_as_date=False)
        if divs.empty:
            divs.to_csv(f"{directory}/{filename}")
            logger.logging.debug(f"{ticker} dividends loaded from yfinance api")
        else:
            divs.set_index("date", inplace=True)
            divs.to_csv(f"{directory}/{filename}")
            logger.logging.debug(f"{ticker} dividends loaded from yfinance api")

    @staticmethod
    def _make_ptf_currency_df():
        dates = pd.date_range(start=datetime(2000, 1, 1), end=datetime.today())
        data = [1 for _ in range(len(dates))]
        return pd.DataFrame(data=data, index=pd.Index(name='Date', data=dates), columns=['Close'])

    @staticmethod
    def _convert_ticker(ticker):
        ticker = ticker.replace('.TRT', '.TO')
        ticker = ticker.replace(' ', '')
        ticker = ticker.replace('.UN', '-UN')
        ticker = ticker.replace('.VN', '.V')
        return ticker
