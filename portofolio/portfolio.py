from datetime import datetime
from typing import Union, List
from portofolio.position import Position
from portofolio.helpers.cash_account import CashAccount
from portofolio.data_sources.data_reader import DataReader
from portofolio.helpers.fx_rates import FxRates
from portofolio.helpers.transaction import Transaction
from portofolio.helpers.transaction_manager import TransactionManager
from portofolio.utils import dates_utils, logger, df_utils
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

        self.start_date = None
        # load data        
        self.load_data()

    def __repr__(self):
        return self.account

    def load_data(self) -> None:
        """

        :return:
        """
        self._transaction_manager.fetch()
        self.start_date = self._transaction_manager.first_trx_date()
        self._load_positions()
        self._load_position_quantities()
        self._load_market_value()
        logger.logging.debug(f'{self.account} data loaded')

    def update_data(self) -> None:
        """

        :return:
        """
        self._refresh_prices()
        self._refresh_fx()
        self.load_data()
        logger.logging.debug(f'{self.account} updated')

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
                pos_val = position.get_quantities().shift(1).fillna(method="backfill").multiply(position.get_prices().loc[self.start_date:])
                pos_val = pos_val.fillna(method='ffill')
                market_value = market_value.add(pos_val)
                market_value = market_value.fillna(method='ffill')
            self._market_value = market_value.dropna()
            logger.logging.debug(f'{self.account} market_value computed')
        else:
            logger.logging.debug(f"{self.account} no positions in portfolio")

    @property
    def market_values(self) -> pd.Series:
        return self._market_value

    def _load_positions(self, ) -> None:
        tickers = self._transaction_manager.all_positions()
        for ticker in tickers:
            currency = self._transaction_manager.get_currency(ticker=ticker)
            pos = Position(ticker, currency=currency)

            if self.currency != pos.currency:
                prices = pos.get_prices().multiply(self._fx.get(f"{pos.currency}{self.currency}")).dropna()
                pos.set_prices(prices=prices)
            self._positions[ticker] = pos
        logger.logging.debug(f'positions for {self.account} loaded')

    @property
    def positions(self) -> dict:
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
            logger.logging.debug(f'{self.account} no positions in portfolio')

    def add_transaction(self, transactions: List[Transaction]) -> None:
        """
        add transactions to portfolio
        :param transactions: portofolio transaction object list
        :return: None
        """
        for trx in transactions:
            ok, new_cash = self._check_trx(transaction=trx)

            if not ok:
                logger.logging.error(f'{self.account}: Not enough funds to perform this transaction, missing {-1 * new_cash} to complete')
            else:
                self._transaction_manager.add(transaction=trx)
        self.load_data()

    @property
    def transactions(self) -> pd.DataFrame:
        return self._transaction_manager.get_transactions()

    @property
    def cash_history(self):
        dates = self.market_values.index
        cash = [self.cash(date) for date in dates]
        cash_c = pd.Series(data=cash, index=dates)
        return cash_c

    def add_cash_change(self, date: datetime, direction: str, amount: float) -> None:
        self._cash_account.add_cash_change(date=date, direction=direction, amount=amount)
        logger.logging.info(f'cash change for {self.account} have been added')
        self.load_data()

    def cash(self, date: datetime = None) -> float:
        """
        cash available on given date
        :param date: datetime object
        :return: float
        """
        if date is None:
            date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)

        changes = self._cash_account.get_cash_change(date)

        trx = self.transactions
        trx = trx.loc[trx.index <= date]
        trx_value = trx.Quantity * trx.Price
        trx = pd.concat([trx, trx_value], axis=1)

        trx_currencies = set(trx.Currency)
        for curr in trx_currencies:
            try:
                live_fx = self._fx.get(f'{curr}{self.currency}').loc[date]
            except KeyError:
                raise KeyError("fx data has not been updated")
            trx.loc[trx.Currency == curr, 0] *= live_fx
        values = trx[0].sum() * -1

        fees = trx.Fees.sum()

        dividends = self.dividends(end_date=date)
        cash = values + changes + dividends - fees
        return round(cash, 2)

    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        accumulated dividend over date range
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """
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

    def daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        portfolio return in $ amount
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """
        if end_date is None:
            end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date is None:
            start_date = end_date

        transactions = self._transaction_manager.get_transactions()
        try:
            transactions = transactions.loc[start_date:end_date]
        except KeyError:
            transactions = transactions.loc[start_date:]
        pnl = df_utils.pnl_dict_map(d=self.positions, start_date=start_date, end_date=end_date, transactions=transactions, fx=self._fx.rates)
        return pd.DataFrame.from_dict(pnl, orient="columns").fillna(0)

    def pct_daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None, include_cash: bool = False) -> pd.DataFrame:
        """
        portfolio return in % of market value
        :param include_cash: if we include the cash amount at that time to calc the market value
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """
        if end_date is None:
            end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date is None:
            start_date = end_date

        if include_cash:
            market_vals = self.market_values.loc[start_date:end_date] + self.cash_history
        else:
            market_vals = self.market_values.loc[start_date:end_date]

        pnl = self.daily_total_pnl(start_date, end_date).sum(axis=1).divide(market_vals)
        return pnl

    def reset_transactions(self) -> None:
        self._transaction_manager.reset_transactions()
        logger.logging.debug(f'transactions for {self.account} have been reset')
        self.load_data()

    def reset_cash(self) -> None:
        self._cash_account.reset_cash()
        logger.logging.debug(f'cash for {self.account} have been reset')
        self.load_data()

    @staticmethod
    def _make_qty_series(quantities: Union[pd.Series, pd.DataFrame]) -> Union[pd.Series, pd.DataFrame]:
        return quantities.fillna(0).cumsum()

    def _check_trx(self, transaction) -> tuple:
        value = transaction.quantity * transaction.price

        if transaction.currency != self.currency:
            pair = f"{transaction.currency}{self.currency}"
            value = (value * self._fx.get(pair).loc[transaction.date] + transaction.fees)
        live_cash = self.cash(date=transaction.date)
        new_cash = live_cash - value

        return value < live_cash, new_cash
