from datetime import datetime
from typing import Union

from cash_account import CashAccount
from data_sources.data_reader import DataReader
from fx_rates import FxRates
from position import Position
from transaction import Transaction
from transaction_manager import TransactionManager
from utils import logger, dates_utils, df_utils
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

    def _load_market_value(self) -> None:
        if len(self._positions):
            last_date = self._datareader.last_data_point(self.account, ptf_currency=self.currency)
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

            last_date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)
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
            date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)

        changes = self._cash_account.get_cash_change(date)

        trx = self._transaction_manager.get_transactions()
        trx = trx.loc[trx.index <= date]
        trx.loc[:, 'Value'] = trx.Quantity * trx.Price

        trx_currencies = set(trx.Currency)
        for curr in trx_currencies:
            live_fx = self._fx.get(f'{curr}{self.currency}').loc[date]
            trx.loc[trx.Currency == curr, 'Value'] *= live_fx
        values = trx['Value'].sum() * -1

        fees = trx.Fees.sum()

        dividends = self.dividends(end_date=date)
        cash = values + changes + dividends - fees
        return round(cash, 2)

    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:
        if len(self._positions):
            if end_date is None:
                end_date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)
            if start_date is None:
                start_date = self.start_date
            transactions = self._transaction_manager.get_transactions().loc[start_date:]
            transactions = transactions.loc[transactions.index <= end_date]
            dividends = transactions.loc[transactions.Type == 'Dividend', ['Price', 'Currency']]

            trx_currencies = set(transactions.Currency)
            for curr in trx_currencies:
                live_fx = self._fx.get(f'{curr}{self.currency}').loc[end_date]
                dividends.loc[dividends.Currency == curr, 'Price'] *= live_fx
            return round(dividends['Price'].sum(), 2)
        else:
            return 0

    def daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None):
        transactions = self._transaction_manager.get_transactions()
        pnl = df_utils.pnl_dict_map(d=self.get_position(), start_date=start_date, end_date=end_date, transactions=transactions, fx=self._fx.rates)
        return pd.DataFrame.from_dict(pnl, orient="columns").fillna(0)

    def daily_total_pnl_pct(self, start_date: datetime = None, end_date: datetime = None):
        pnl = self.daily_total_pnl(start_date, end_date).sum(axis=1).divide(self.get_market_value().loc[start_date:end_date])
        return pnl

    @staticmethod
    def _make_qty_series(quantities: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
        return quantities.fillna(0).cumsum()
