from datetime import datetime
from typing import List, Union
from cash_account import CashAccount
from data_sources.data_reader import DataReader
from fx_rates import FxRates
from position import Position
from transaction import Transaction
from transaction_manager import TransactionManager
from utils import logger, dates_utils
import pandas as pd


class Portfolio(object):

    def __init__(self, account: str, currency: str):
        # attributes
        self.account = account
        self._positions = {}
        self.currency = currency
        self._market_value = pd.Series()

        # helpers
        self._cash_account = CashAccount(account=self.account)
        self._datareader = DataReader()
        self._transaction_manager = TransactionManager(account=self.account)
        self._fx = FxRates(ptf_currency=currency, currencies=self._transaction_manager.get_currencies())

        self.start_date = self._transaction_manager.first_trx_date()
        # load data        
        self.load_data()

    def __repr__(self):
        return self.account

    def load_data(self) -> None:
        self._transaction_manager.fetch()
        self._load_positions()
        self._load_position_quantities()
        self._load_market_value()
        logger.logging.info(f'{self.account} data loaded')

    def update_data(self) -> None:
        self._refresh_prices()
        self._refresh_fx()
        self.load_data()
        self._transaction_manager.fetch()
        logger.logging.info(f'{self.account} updated')

    def _refresh_fx(self) -> None:
        self._fx.refresh()

    def _refresh_prices(self) -> None:
        for ticker in self._positions.keys():
            self._datareader.update_prices(ticker=ticker)

    def _load_market_value(self) -> None:  # FIXME make for a specific date, not a time series, attribute?
        if len(self._positions):
            last_date = self._datareader.last_data_point(self.account)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            market_value = pd.Series(index=dates, data=[0 for _ in range(len(dates))])

            for position in self._positions.values():
                pos_val = position.get_quantities().multiply(position.get_prices().loc[self.start_date:])
                pos_val = pos_val.fillna(method='ffill')
                market_value = market_value.add(pos_val)
                market_value = market_value.fillna(method='ffill')
            self._market_value = market_value.dropna()
            logger.logging.debug(f'{self.account} market_value computed')
        else:
            logger.logging.info(f"{self.account} no positions in portfolio")

    def get_market_value(self) -> pd.Series:
        return self._market_value

    def _load_positions(self, ) -> None:
        tickers = self._transaction_manager.all_positions()
        for ticker in tickers:
            currency = self._transaction_manager.get_currency(ticker=ticker)
            pos = Position(ticker, currency=currency, datareader=self._datareader)

            if self.currency != pos.currency:
                prices = pos.get_prices().multiply(self._fx.get(f"{pos.currency}{self.currency}")).dropna()
                pos.set_prices(prices=prices)
            self._positions[ticker] = pos
        logger.logging.debug(f'positions for {self.account} loaded')

    def get_position(self, ticker: str = None) -> Union[Position, dict]:
        if ticker:
            return self._positions.get(ticker)
        else:
            return self._positions

    def _load_position_quantities(self) -> None:
        if len(self._positions):

            last_date = self._datareader.last_data_point(account=self.account)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            date_merge = pd.DataFrame(index=dates, columns=['qty'])

            for position in self._positions.values():
                trx = self._transaction_manager.transactions.loc[
                    (self._transaction_manager.transactions.Ticker == position.ticker)
                    & (self._transaction_manager.transactions.Type != 'Dividend')]
                date_merge.loc[:, 'qty'] = trx['Quantity']
                pos_qty = self._make_qty_series(date_merge.loc[:, 'qty'])
                position.set_quantities(pos_qty)
            logger.logging.debug(f'{self.account} quantities computed')

        else:
            logger.logging.info(f'{self.account} no positions in portfolio')

    def add_transaction(self, transaction: Transaction) -> None:
        value = transaction.quantity * transaction.price
        pair = f"{transaction.currency}{self.currency}"
        if transaction.currency != self.currency:
            value = (value * self._fx.get(pair).loc[transaction.date] + transaction.fees).iloc[0]
        live_cash = self.cash(date=transaction.date)
        new_cash = live_cash - value
        if value > live_cash:
            logger.logging.error(f'{self.account}: Not enough funds to perform this transaction, missing {-1 * new_cash} to complete')
        else:
            self._transaction_manager.add(transaction=transaction)

    def cash(self, date: datetime = None) -> float:
        if date is None:
            date = self._datareader.last_data_point(account=self.account)

        live_fx = self._fx.get(f'USD{self.currency}').loc[date].iloc[0]  # FIXME for any ptf _fx.. vectorized
        changes = self.cash_account.get_cash_change(date)

        trx = self._transaction_manager.get_transactions()
        trx = trx.loc[trx.index <= date,]
        trx.loc[:, 'Value'] = trx.Quantity * trx.Price
        trx.loc[trx.Currency == 'USD', 'Value'] *= live_fx
        values = trx['Value'].sum() * -1

        fees = trx.Fees.sum()

        dividends = self.dividends(end_date=date)

        return values + changes + dividends - fees

    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:  # FIXME for any ptf _fx
        if len(self._positions):
            if end_date is None:
                end_date = self._datareader.last_data_point(account=self.account)
            if start_date is None:
                start_date = self.start_date
            live_fx = self._fx.get(f'USD{self.currency}').loc[end_date].iloc[0]
            transactions = self._transaction_manager.get_transactions().loc[
                (self._transaction_manager.get_transactions().index <= end_date) & (
                        self._transaction_manager.get_transactions().index >= start_date),]
            dividends = transactions.loc[transactions.Type == 'Dividend', ['Price', 'Currency']]
            dividends.loc[dividends.Currency == 'USD', 'Price'] *= live_fx
            return dividends['Price'].sum()
        else:
            return 0

    def total_pnl(self):
        raise NotImplementedError

    def pnl(self):
        raise NotImplementedError

    @staticmethod
    def _make_qty_series(quantities: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
        return quantities.fillna(0).cumsum()

