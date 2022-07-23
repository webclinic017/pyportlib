from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Union

import pandas as pd

from position import Position
from pyportlib import Transaction, CashChange


class IPortfolio(ABC):

    @abstractmethod
    def load_data(self) -> None:
        """
        Loads Portfolio object with current available data, mostly used to update some attributes
        dependent on other objects or computations

        :return: None
        """

    @abstractmethod
    def update_data(self, fundamentals_and_dividends: bool = False) -> None:
        """
        Updates all of the market data of the portfolio (prices, fx)

        :param fundamentals_and_dividends: True to update all statement and dividend data
        :return:
        """

    @abstractmethod
    def compute_market_value(self, positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.Series:
        """
        Computes the daily market value of the portfolio

        :param positions_to_exclude: Ticker of position to exclude from computations
        :param tags: Tags to compute the market value of. If None, it will be the market value of the whole portfolio
        :return:
        """

    @property
    @abstractmethod
    def market_value(self) -> pd.Series:
        """Portfolio market value"""

    @abstractmethod
    def position_tags(self):
        """Position tags"""

    @property
    @abstractmethod
    def positions(self) -> Dict[str, Position]:
        """Portfolio Positions"""

    @abstractmethod
    def add_transaction(self, transactions: Union[Transaction, List[Transaction]]) -> None:
        """
        Add transactions to portfolio and save transaction file

        :param transactions: pyportlib transaction object, single or list
        :return: None
        """

    @property
    @abstractmethod
    def transactions(self) -> pd.DataFrame:
        """"""

    @property
    @abstractmethod
    def cash_changes(self) -> pd.DataFrame:
        """"""

    @property
    @abstractmethod
    def cash_history(self):
        """"""

    @abstractmethod
    def add_cash_change(self, cash_changes: Union[List[CashChange], CashChange]) -> None:
        """
        Add cash change (deposit or withdrawal) to portfolio through the CashChange object

        :return: None
        """

    @abstractmethod
    def cash(self, date: datetime = None) -> float:
        """
        Cash available on given date

        :param date: datetime
        :return: float
        """

    @abstractmethod
    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        Accumulated dividend over date range for the entire portfolio

        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :return:
        """

    @abstractmethod
    def daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None,
                        positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.DataFrame:
        """
        Portfolio return per position in $ amount for specified date range

        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :param positions_to_exclude: List of ticker to exclude from calculation
        :param tags: List of tags to compute return for
        :return:
        """

    @abstractmethod
    def pct_daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None,
                            include_cash: bool = False,
                            positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.Series:
        """
        Portfolio return in % of market value

        :param start_date: start date of series (if only param, end_date is last date)
        :param end_date: start date of series (if only param, end_date the only date given in series)
        :param include_cash: If we include the cash amount at that time to calc the market value
        :param tags: Specific position tags to compute
        :param positions_to_exclude: List of tickers to exlude from computation
        :return:
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Resets transactions and cash flows from the portfolio object and erases the saved csv files associated to
        the portfolio

        :return: None
        """

    @abstractmethod
    def corr(self, lookback: str = None, date: datetime = None):
        """
        Open positions correlations

        :param lookback:
        :param date:
        :return:
        """

    @abstractmethod
    def position_weights(self, date: datetime = None) -> pd.Series:
        """
        Portfolio position weights in %

        :param date:
        :return:
        """

    @abstractmethod
    def strategy_weights(self, date: datetime = None) -> pd.Series:
        """
        Portfolio strategy tags weights in %

        :param date:
        :return:
        """

    @abstractmethod
    def open_positions(self, date: datetime) -> Dict[str, Position]:
        """
        Dict with only active position on given date

        :param date: Date to get open positions from
        :return:
        """

    @abstractmethod
    def open_positions_returns(self, lookback: str = None, date: datetime = None):
        """
        Get returns from open positions on given date

        :param lookback: ex. 1y or 10m to lookback from given date argument
        :param date: last business day if none
        :return:
        """
