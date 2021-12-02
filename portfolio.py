from datetime import datetime
from typing import List, Union
import numpy as np
from data_sources.data_reader import DataReader
from position import Position
from transaction import Transaction
from transaction_manager import TransactionManager
from utils import logger, dates_utils
import pandas as pd


class Portfolio(object):

    def __init__(self, account: str, load_data: bool = False):

        self.account = account
        self.positions = {}
        self.fx = {}
        self.prices_df = pd.DataFrame()
        self.quantities = pd.DataFrame()
        self.market_value = pd.DataFrame()
        self.cash = 1000000000  # TODO make cash management so changes are saved, and cash can be tracked like a position
        self.datareader = DataReader()
        self.transaction_manager = TransactionManager(account=self.account)
        self.start = None
        self.load_positions()
        if load_data:
            self.load_position_prices()
            self.load_fx()
            self.load_prices_df()
            self.get_quantities()
            self.get_market_value()

    def __repr__(self):
        return self.account

    def get_position(self, ticker: str = None) -> Union[Position, dict]:
        if ticker:
            return self.positions.get(ticker)
        else:
            return self.positions

    def refresh_all(self):
        for ticker in self.positions.keys():
            self.datareader.update_prices(ticker=ticker)

        self.datareader.update_fx(currency='USD')
        self.load_positions()
        self.load_position_prices()
        self.load_fx()
        self.load_prices_df()
        self.get_quantities()
        logger.logging.info(f'{self.account} refreshed')

    def get_market_value(self):
        if self.market_value.empty:
            last_date = self.datareader.last_data_point()
            first_date = self.transaction_manager.first_trx_date()
            date = dates_utils.get_market_days(start=first_date, end=last_date)
            market_value = pd.Series(index=date, data=[0 for _ in range(len(date))])

            for position in self.positions.keys():
                pos = self.get_position(position)
                pos_val = self.quantities[position]*pos.prices_cad.iloc[:, 0]

                if pos_val.iloc[0] == np.nan:
                    pos_val.iloc[0] = 0
                pos_val = pos_val.fillna(method='ffill')
                pos.market_val = pos_val
                market_value += pos_val
                market_value = market_value.fillna(0)
            self.market_value = market_value
            logger.logging.info(f'{self.account} market_value computed')

        return self.market_value

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
        first_trx = self.transaction_manager.first_trx_date()
        for position in self.positions.keys():
            pos = self.get_position(position)
            pos.get_prices_cad(start_date=first_trx)
            logger.logging.info(f'{position} loaded')

    def load_prices_df(self):
        if self.prices_df.empty:
            pos = list(self.get_position().values())
            df = self._make_df(pos)

            self.prices_df = df.dropna(how='all').sort_index()
            logger.logging.info(f'{self.account}" transactions from {self.prices_df.index.min().date()} to {self.prices_df.index.max().date()}')
        return self.prices_df

    def add_transaction(self, transaction: Transaction) -> None:
        value = transaction.quantity * transaction.price

        if transaction.currency != 'CAD':
            value = (value * self.fx.get(transaction.currency).loc[transaction.date] + transaction.fees).iloc[0]
        new_cash = self.cash - value
        if value > self.cash:
            logger.logging.error(f'Not enough funds to perform this transaction, missing {-1*new_cash} to complete')
        else:
            self.cash = new_cash
            self.transaction_manager.add(transaction=transaction)

    def get_quantities(self):
        last_date = self.datareader.last_data_point()
        first_date = self.transaction_manager.first_trx_date()
        for position in self.positions.keys():
            trx = self.transaction_manager.transactions.loc[(self.transaction_manager.transactions.Ticker == position)
                                                            & (self.transaction_manager.transactions.Type != 'Dividend')]
            quantity = self._make_position_qty(trx, first_date, last_date)
            self.quantities[position] = quantity
            logger.logging.info(f'quantities computed for {position}')

    @staticmethod
    def _make_position_qty(transactions: pd.DataFrame, start: datetime, end: datetime):
        date = dates_utils.get_market_days(start=start, end=end)
        quantity = pd.DataFrame(index=date, columns=['Quantity'])
        # TODO optimise, maybe do cumsum in get_quantities (only once), etc
        return pd.concat([transactions['Quantity'], quantity], axis=1).fillna(0).cumsum().iloc[:, 0]

    @staticmethod
    def _make_df(positions: List[Position]):
        df = positions[0].get_prices_cad()
        df.columns = [positions[0].ticker]

        for pos in positions[1:]:
            prices = pos.get_prices_cad()
            prices.columns = [pos.ticker]
            df = pd.merge(df, prices, how='outer', on='Date')
        return df
