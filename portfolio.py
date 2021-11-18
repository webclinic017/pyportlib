from typing import List, Union

from data_sources.data_reader import DataReader
from position import Position
from transaction_manager import TransactionManager
from utils import logger
import pandas as pd


class Portfolio(object):

    def __init__(self, account: str, load_data: bool = False):

        self.account = account
        self.positions = {}
        self.fx = {}
        self.prices_df = None
        self.datareader = DataReader()
        self.transaction_manager = TransactionManager(account=self.account)
        self.load_positions()
        if load_data:
            self.load_position_prices()
            self.load_fx()
            self.load_prices_df()

    def __repr__(self):
        return self.account

    def get_position(self, ticker: str = None) -> Union[Position, dict]:
        if ticker:
            return self.positions.get(ticker)
        else:
            return self.positions

    def load_positions(self):
        tickers = self.transaction_manager.all_positions()
        for ticker in tickers:
            currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
            self.positions[ticker] = Position(ticker, currency=currency, datareader=self.datareader)
        logger.logging.info(f'positions for {self.account} loaded')

    def load_fx(self):
        if not self.fx:
            currencies = self.transaction_manager.get_currencies()

            for curr in currencies:
                self.fx[curr] = self.datareader.read_fx(currency=curr)
            logger.logging.info(f'fx for {self.account} loaded')
        return self.fx

    def load_position_prices(self):
        for position in self.positions.keys():
            pos = self.get_position(position)
            first_trx = self.transaction_manager.first_trx_date(ticker=pos.ticker)
            pos.get_prices_cad(start_date=first_trx)
            logger.logging.info(f'{position} loaded')

    def load_prices_df(self):
        if self.prices_df is None:
            pos = list(self.get_position().values())
            df = self.make_df(pos)

            self.prices_df = df.dropna(how='all').sort_index()
            logger.logging.info(f'{self.account}" transactions from {self.prices_df.index.min().date()} to {self.prices_df.index.max().date()}')
        return self.prices_df

    @staticmethod
    def make_df(positions: List[Position]):
        df = positions[0].get_prices_cad()
        df.columns = [positions[0].ticker]

        for pos in positions[1:]:
            prices = pos.get_prices_cad()
            prices.columns = [pos.ticker]
            df = pd.merge(df, prices, how='outer', on='Date')
        return df
