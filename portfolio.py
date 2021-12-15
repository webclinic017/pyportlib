from datetime import datetime
from typing import List, Union
import numpy as np

from cash_account import CashAccount
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
        self.prices = pd.DataFrame()
        self.quantities = pd.DataFrame()
        self.market_value = pd.DataFrame()
        self.cash = CashAccount(account=self.account)
        self.datareader = DataReader()
        self.transaction_manager = TransactionManager(account=self.account)
        self.start = self.transaction_manager.first_trx_date()
        if load_data:
            self.load_data()

    def __repr__(self):
        return self.account

    def load_data(self, reload: bool = False) -> None:
        self._load_fx(reload=reload)
        self._load_positions(reload=reload)
        self._load_prices(reload=reload)
        self._load_quantities(reload=reload)
        self._load_market_value(reload=reload)
        logger.logging.info(f'{self.account} data loaded')

    def refresh_all(self) -> None:
        self._refresh_prices()
        self._refresh_fx()
        self._load_prices()
        self._load_quantities()
        self._load_market_value(reload=False)
        logger.logging.info(f'{self.account} refreshed')

    def _refresh_fx(self) -> None:
        currencies = self.transaction_manager.get_currencies()
        for curr in currencies:
            self.fx[curr] = self.datareader.update_fx(currency=curr)
        self._load_fx(reload=True)

    def _refresh_prices(self) -> None:
        for ticker in self.positions.keys():
            self.datareader.update_prices(ticker=ticker)
        self._load_positions(reload=True)

    def _load_fx(self, reload: bool = False) -> None:
        if not self.fx or reload:
            currencies = self.transaction_manager.get_currencies()

            for curr in currencies:
                self.fx[curr] = self.datareader.read_fx(currency=curr)
            logger.logging.info(f'fx for {self.account} loaded')

    def get_fx(self):
        return self.fx

    def _load_market_value(self, reload: bool = False) -> None:
        if self.market_value.empty or reload:
            last_date = self.datareader.last_data_point(self.account)
            first_date = self.start
            dates = dates_utils.get_market_days(start=first_date, end=last_date)
            market_value = pd.Series(index=dates, data=[0 for _ in range(len(dates))])

            for position in self.positions.keys():
                pos = self.get_position(position)
                pos_val = self.quantities[position] * pos.get_prices_cad().iloc[:, 0]

                pos_val = pos_val.fillna(method='ffill')
                # pos.set_market_value(market_value=pos_val)
                market_value += pos_val
                market_value = market_value.fillna(method='ffill')
            self.market_value = market_value
            logger.logging.info(f'{self.account} market_value computed')

    def get_market_value(self):
        return self.market_value

    def _load_positions(self, reload: bool = False) -> None:
        first_trx = self.transaction_manager.first_trx_date()
        tickers = self.transaction_manager.all_positions()
        for ticker in tickers:
            currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
            pos = Position(ticker, currency=currency, datareader=self.datareader)
            pos.get_prices_cad(start_date=first_trx, reload=reload)
            self.positions[ticker] = pos
        logger.logging.info(f'positions for {self.account} loaded')

    def get_position(self, ticker: str = None) -> Union[Position, dict]:
        if ticker:
            return self.positions.get(ticker)
        else:
            return self.positions

    def _load_prices(self, reload: bool = False) -> None:
        if self.prices.empty or reload:
            pos = list(self.get_position().values())
            self.prices = self._make_prices_df(pos)

            logger.logging.info(
                f'{self.account} transactions from {self.prices.index.min().date()} to {self.prices.index.max().date()}')

    def get_prices(self):
        return self.prices

    def _load_quantities(self, reload: bool = False) -> None:
        if self.quantities.empty or reload:
            last_date = self.datareader.last_data_point(account=self.account)
            first_date = self.transaction_manager.first_trx_date()
            dates = dates_utils.get_market_days(start=first_date, end=last_date)
            self.quantities.index = dates

            for position in self.positions.keys():
                trx = self.transaction_manager.transactions.loc[(self.transaction_manager.transactions.Ticker == position)
                                                                & (
                                                                            self.transaction_manager.transactions.Type != 'Dividend')]
                self.quantities[position] = trx['Quantity']
                logger.logging.info(f'quantities computed for {position}')

            self.quantities = self.quantities.fillna(0).cumsum()

    def get_quantities(self):
        return self.quantities

    def add_transaction(self, transaction: Transaction) -> None:
        value = transaction.quantity * transaction.price

        if transaction.currency != 'CAD':
            value = (value * self.fx.get(transaction.currency).loc[transaction.date] + transaction.fees).iloc[0]
        new_cash = self.cash - value  # TODO cash calc
        if value > self.cash:
            logger.logging.error(f'Not enough funds to perform this transaction, missing {-1 * new_cash} to complete')
        else:
            self.cash = new_cash
            self.transaction_manager.add(transaction=transaction)

    @staticmethod
    def _make_prices_df(positions: List[Position]):
        df = positions[0].get_prices_cad()
        df.columns = [positions[0].ticker]

        for pos in positions[1:]:
            prices = pos.get_prices_cad()
            prices.columns = [pos.ticker]
            df = pd.merge(df, prices, how='outer', on='Date')
        return df.dropna(how='all').sort_index()
