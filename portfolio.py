from data_sources.data_source_manager import DataSourceManager
from position import Position
from transaction_manager import TransactionManager
import pandas as pd
from utils import logger


class Portfolio(object):

    def __init__(self, account: str):

        self.account = account
        self.positions = {}
        self.connection = DataSourceManager()
        self.transaction_manager = TransactionManager(account=self.account, connection=self.connection)
        self.load_positions()
        self.prices_df = pd.DataFrame()

    def __repr__(self):
        return self.account

    def get_position(self, ticker):
        return self.positions.get(ticker)

    def load_positions(self):
        tickers = self.transaction_manager.all_tickers()
        for ticker in tickers:
            currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
            self.positions[ticker] = Position(ticker, currency=currency, connection=self.connection)
        logger.logging.info(f'positions for {self.account} loaded')

    def load_prices(self, read: bool):
        if not read:
            self.connection.refresh_fx('USD')
        for position in self.positions.keys():
            pos = self.get_position(position)
            pos.load_prices_cad(read=read)
            logger.logging.info(f'{position} loaded')
        self.load_prices_df()

    def load_prices_df(self):
        if self.prices_df.empty:
            first_pos = self.positions[list(self.positions.keys())[0]]
            df = first_pos.prices_cad
            df.columns = [first_pos.ticker]
            for position in list(self.positions.values())[1:]:
                prices = position.prices_cad
                prices.columns = [position.ticker]
                df = pd.merge(df, prices, how='outer', on='Date')
            self.prices_df = df.dropna(how='all').sort_index()
            logger.logging.info(f'most recent data point: {self.prices_df.index.max()}')
        return self.prices_df
