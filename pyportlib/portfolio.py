from datetime import datetime
from typing import Union, List, Dict

from .helpers.cash_change import CashChange
from .position import Position
from .helpers.cash_manager import CashManager
from .data_sources.data_reader import DataReader
from .helpers.fx_rates import FxRates
from .helpers.transaction import Transaction
from .helpers.transaction_manager import TransactionManager
from .utils import dates_utils, logger, ts
import pandas as pd


class Portfolio:

    def __init__(self, account: str, currency: str):
        # attributes
        self.account = account
        self._positions = {}
        self.currency = currency.upper()
        self._market_value = pd.Series()
        self._cash_history = pd.Series()

        # helpers
        self._cash_manager = CashManager(account=self.account)
        self._datareader = DataReader()
        self._transaction_manager = TransactionManager(account=self.account)
        self._fx = FxRates(ptf_currency=currency, currencies=self._transaction_manager.get_currencies())

        self.start_date = None
        # load data        
        self.load_data()
        self._load_cash_history()

    @property
    def name(self):
        return "portfolio"

    def __repr__(self):
        return self.account

    def load_data(self) -> None:
        """
        Loads Portfolio object with current available data, mostly used to update some attributes
        dependent on other objects or computations
        :return: None
        """
        self.start_date = self._transaction_manager.first_trx()
        self._fx.set_pairs(pairs=[f"{curr}{self.currency}" for curr in self._transaction_manager.get_currencies()])

        self._cash_manager.load()
        self._transaction_manager.load()
        self._load_positions()
        self._load_position_quantities()
        self._load_market_value()

        logger.logging.debug(f'{self.account} data loaded')

    def update_data(self, fundamentals_and_dividends: bool = False) -> None:
        """
        Updates all of the market data of the portfolio (prices, fx)
        :param fundamentals_and_dividends: True to update all statement and dividend data
        :return:
        """
        self._update_positions(fundamentals_and_dividends=fundamentals_and_dividends)
        self._update_fx()
        self.load_data()
        logger.logging.info(f'{self.account} updated')

    def _update_fx(self) -> None:
        self._fx.refresh()

    def _update_positions(self, fundamentals_and_dividends: bool = True) -> None:
        for position in self._positions.values():
            position.update_data(fundamentals_and_dividends=fundamentals_and_dividends)

    def _load_market_value(self, **kwargs) -> None:
        self._market_value = pd.Series()
        positions_to_compute = self.positions
        return_flag = False

        # used for pnl what if scenarios where position are easily ommited from calculations
        if kwargs.get('positions_to_exclude'):
            positions_ = set(positions_to_compute.keys()) - set(kwargs.get('positions_to_exclude'))
            positions_to_compute = {k: positions_to_compute[k] for k in positions_}
            return_flag = True

        if len(positions_to_compute):
            last_date = self._datareader.last_data_point(self.account, ptf_currency=self.currency)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            market_value = pd.Series(index=dates, data=[0 for _ in range(len(dates))])

            for position in positions_to_compute.values():
                pos_val = position.quantities.shift(1).fillna(method="backfill").multiply(
                    position.prices.loc[self.start_date:])
                pos_val = pos_val.fillna(method='ffill')
                pos_val = pos_val.fillna(0)
                if pos_val.sum() != 0:
                    market_value = market_value.add(pos_val)
                    market_value = market_value.fillna(method='ffill')
                else:
                    logger.logging.error(f'no market value computed for {position.ticker}')

            # used by pnl to return the value instead of setting it
            if return_flag:
                logger.logging.debug(f'{self.account} market_value computed')
                return market_value.dropna()
            elif not return_flag:
                self._market_value = market_value.dropna()
                logger.logging.debug(f'{self.account} market_value computed and set')
        else:
            logger.logging.debug(f"{self.account} no positions in portfolio")

    @property
    def market_values(self) -> pd.Series:
        return self._market_value

    def _load_positions(self) -> None:
        """
        Based on on the transaction data, loads all of the active and closed positions
        :return: None
        """
        self._positions = {}
        tickers = self._transaction_manager.all_positions()
        for ticker in tickers:
            currency = self._transaction_manager.get_currency(ticker=ticker)
            pos = Position(ticker, local_currency=currency)

            if self.currency != pos.currency:
                prices = pos.prices.multiply(self._fx.get(f"{pos.currency}{self.currency}"), fill_value=None).dropna()
                pos.prices = prices
            self._positions[ticker] = pos
        logger.logging.debug(f'positions for {self.account} loaded')

    @property
    def positions(self) -> Dict[str, Position]:
        return self._positions

    def _load_position_quantities(self) -> None:
        """
        Based on the transaction data, loads all of the active and closed positions
        :return: None
        """
        if len(self._positions):

            last_date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            date_merge = pd.DataFrame(index=dates, columns=['qty'])

            for position in self._positions.values():
                trx = self._transaction_manager.transactions.loc[
                    (self._transaction_manager.transactions.Ticker == position.ticker)
                    & (self._transaction_manager.transactions.Type != 'Dividend')]

                date_merge.loc[:, 'qty'] = trx[['Quantity']].reset_index().groupby('Date').sum()

                pos_qty = self._make_qty_series(date_merge.loc[:, 'qty'])
                position.quantities = pos_qty
            logger.logging.debug(f'{self.account} quantities computed')

        else:
            logger.logging.debug(f'{self.account} no positions in portfolio')

    def add_transaction(self, transactions: Union[Transaction, List[Transaction]]) -> None:
        """
        Add transactions to portfolio
        :param transactions: pyportlib transaction object, single or list
        :return: None
        """
        if transactions:
            if not hasattr(transactions, '__iter__'):
                transactions = [transactions]

            for trx in transactions:
                ok, new_cash = self._check_trx(transaction=trx)

                if not ok:
                    logger.logging.error(f'{self.account}: transaction not added. not enough funds to perform this transaction, missing {-1 * new_cash} to complete')
                else:
                    self._transaction_manager.add(transaction=trx)
            self.load_data()

    @property
    def transactions(self) -> pd.DataFrame:
        return self._transaction_manager.transactions

    @property
    def cash_changes(self) -> pd.DataFrame:
        return self._cash_manager.cash_changes

    @property
    def cash_history(self):
        return self._cash_history

    def _load_cash_history(self):
        """
        Computes cash account for every date
        :return:
        """
        dates = self.market_values.index
        cash = [self.cash(date) for date in dates]
        cash_c = pd.Series(data=cash, index=dates)
        self._cash_history = cash_c

    def add_cash_change(self, cash_changes: Union[List[CashChange], CashChange]) -> None:
        """
        add a cash deposit or withdrawal from the account
        dict need to include {date: datetime,
                              direction: str = "withdrawal", "deposit",
                              amount: float}
        :return: None
        """
        if cash_changes:
            self._cash_manager.add(cash_changes)
            logger.logging.info(f'cash change for {self.account} have been added')
            self.load_data()
            self._load_cash_history()

    def cash(self, date: datetime = None) -> float:
        """
        Cash available on given date
        :param date: datetime
        :return: float
        """
        if date is None:
            date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)

        changes = self._cash_manager.get_cash_change(date)

        trx = self.transactions
        trx = trx.loc[trx.index <= date]
        trx_values = trx.Quantity * trx.Price
        trx = pd.concat([trx, trx_values], axis=1).sort_index()
        trx_currencies = set(trx.Currency)
        for curr in trx_currencies:
            trx_idx = trx.loc[trx.Currency == curr, 0].index

            live_fx = self._fx.get(f'{curr}{self.currency}').reindex(trx_idx, method='ffill')
            trx.loc[trx.Currency == curr, 0] = trx.loc[trx.Currency == curr, 0].multiply(live_fx)

        values = trx[0].sum() * -1

        fees = trx.Fees.sum()

        dividends = self.dividends(end_date=date)
        cash = values + changes + dividends - fees
        return round(cash, 2)

    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        Accumulated dividend over date range for the entire portfolio
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """
        if len(self._positions):
            if end_date is None:
                end_date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)
            if start_date is None:
                start_date = self.start_date
            transactions = self.transactions.loc[start_date:]
            transactions = transactions.loc[transactions.index <= end_date]
            dividends = transactions.loc[transactions.Type == 'Dividend', ['Price', 'Currency']]

            trx_currencies = set(transactions.Currency)
            for curr in trx_currencies:
                try:
                    live_fx = self._fx.get(f'{curr}{self.currency}').loc[end_date]
                except KeyError:
                    logger.logging.debug('live fx request on holiday, key error')
                    live_fx = self._fx.get(f'{curr}{self.currency}').iloc[-1]
                dividends.loc[dividends.Currency == curr, 'Price'] *= live_fx
            return round(dividends['Price'].sum(), 2)
        else:
            return 0

    def daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None, **kwargs) -> pd.DataFrame:
        """
        Portfolio return per position in $ amount for specified date range
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """
        if end_date is None:
            end_date = self._datareader.last_data_point(self.account, ptf_currency=self.currency)
        if start_date is None:
            start_date = end_date

        positions_to_compute = self.positions

        if kwargs.get('positions_to_exclude'):
            positions_ = set(positions_to_compute.keys()) - set(kwargs.get('positions_to_exclude'))
            positions_to_compute = {k: positions_to_compute[k] for k in positions_}

        transactions = self.transactions.loc[self.transactions.Ticker.isin(positions_to_compute.keys())]
        try:
            transactions = transactions.loc[start_date:end_date]
        except KeyError:
            transactions = transactions.loc[transactions.index >= start_date]

        pnl = self._pnl_pos_apply(d=positions_to_compute, start_date=start_date, end_date=end_date, transactions=transactions, fx=self._fx.rates)
        return pnl

    def pct_daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None, include_cash: bool = False,
                            **kwargs) -> pd.Series:
        """
        Portfolio return in % of market value
        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :param include_cash: If we include the cash amount at that time to calc the market value
        :return:
        """
        if end_date is None:
            end_date = self._datareader.last_data_point(self.account, ptf_currency=self.currency)
        if start_date is None:
            start_date = end_date

        if include_cash:
            market_vals = self.market_values.loc[start_date:end_date] + self._cash_history
        else:
            market_vals = self.market_values.loc[start_date:end_date]

        pnl = self.daily_total_pnl(start_date, end_date, **kwargs).sum(axis=1).divide(market_vals).dropna()
        pnl.name = self.account
        return pnl

    def reset(self) -> None:
        """
        Resets transactions and cash flows from the portfolio object and erases the saved csv files associated to
        the portfolio
        :return: None
        """
        self._transaction_manager.reset()
        self._cash_manager.reset()
        self._fx.reset()
        self.load_data()

    def corr(self, lookback: str = None, date: datetime = None):
        """
        Open positions correlations
        :param lookback:
        :param date:
        :return:
        """
        return self.open_positions_returns(lookback=lookback, date=date).corr()

    def weights(self, date: datetime = None):
        """
        Portfolio position weights in %
        :param date:
        :return:
        """
        if date is None:
            date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)

        port_mv = self.market_values.loc[date]
        weights_dict = {k: round(v.npv().loc[date] / port_mv, 5) for k, v in self.positions.items() if
                        v.npv().loc[date] != 0}
        if not 0.9999 < sum(weights_dict.values()) < 1.001:
            raise ValueError(f'weights ({sum(weights_dict.values())}) do not add to 1')
        return weights_dict

    def open_positions(self, date: datetime) -> Dict[str, Position]:
        """
        Dict with only active position on given date
        :param date: Date to get open positions from
        :return:
        """
        return {k: v for k, v in self.positions.items() if round(v.quantities.loc[date]) != 0.}

    def open_positions_returns(self, lookback: str = None, date: datetime = None):
        """
        Get returns from open positions on given date
        :param lookback: ex. 1y or 10m to lookback from given date argument
        :param date: last business day if none
        :return:
        """
        if date is None:
            date = self._datareader.last_data_point(account=self.account, ptf_currency=self.currency)
        if lookback is None:
            lookback = "1y"
        open_positions = self.open_positions(date)
        prices = {k: ts.prep_returns(v, date=date, lookback=lookback) for k, v in open_positions.items()}
        return pd.DataFrame(prices).fillna(0)

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

    @staticmethod
    def _pnl_pos_apply(positions_dict: dict, start_date: datetime, end_date: datetime, transactions: pd.DataFrame, fx: dict) -> pd.DataFrame:
        """
        Apply pnl function to values of position dict and return portfolio pnl df
        :param positions_dict: positions dict
        :param start_date:
        :param end_date:
        :param transactions: transaction to take into account on the pnl
        :param fx: fx df
        :return: pnl df
        """

        pnl = {k: v.daily_pnl(start_date, end_date, transactions.loc[transactions.Ticker == k], fx)['total'] for k, v in positions_dict.items()}
        return pd.DataFrame.from_dict(pnl, orient="columns").fillna(0)
