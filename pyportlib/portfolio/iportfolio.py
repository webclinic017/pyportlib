from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Union

import pandas as pd

from pyportlib.position.iposition import IPosition
from pyportlib import Transaction, CashChange
from pyportlib.utils.time_series import TimeSeriesInterface


class IPortfolio(ABC):
    start_date: Union[datetime, None]

    @abstractmethod
    def load_data(self) -> None:
        """
        """

    @abstractmethod
    def update_data(self, fundamentals_and_dividends: bool = False) -> None:
        """
        """

    @abstractmethod
    def compute_market_value(self, positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.Series:
        """
        """

    @property
    @abstractmethod
    def market_value(self) -> pd.Series:
        """
        """

    @abstractmethod
    def position_tags(self) -> list:
        """
        """

    @property
    @abstractmethod
    def positions(self) -> Dict[str, Union[TimeSeriesInterface, IPosition]]:
        """
        """

    @abstractmethod
    def add_transaction(self, transactions: Union[Transaction, List[Transaction]]) -> None:
        """
        """

    @property
    @abstractmethod
    def transactions(self) -> pd.DataFrame:
        """
        """

    @property
    @abstractmethod
    def cash_changes(self) -> pd.DataFrame:
        """
        """

    @property
    @abstractmethod
    def cash_history(self) -> pd.Series:
        """
        """

    @abstractmethod
    def add_cash_change(self, cash_changes: Union[List[CashChange], CashChange]) -> None:
        """
        """

    @abstractmethod
    def cash(self, date: datetime = None) -> float:
        """
        """

    @abstractmethod
    def dividends(self, start_date: datetime = None, end_date: datetime = None) -> float:
        """
        """

    @abstractmethod
    def daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None,
                        positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def pct_daily_total_pnl(self, start_date: datetime = None, end_date: datetime = None,
                            include_cash: bool = False,
                            positions_to_exclude: List[str] = None, tags: List[str] = None) -> pd.Series:
        """
        """

    @abstractmethod
    def reset(self) -> None:
        """
        """

    @abstractmethod
    def corr(self, lookback: str = None, date: datetime = None) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def position_weights(self, date: datetime = None) -> pd.Series:
        """
        """

    @abstractmethod
    def strategy_weights(self, date: datetime = None) -> pd.Series:
        """
        """

    @abstractmethod
    def open_positions(self, date: datetime) -> Dict[str, Union[TimeSeriesInterface, IPosition]]:
        """
        """

    @abstractmethod
    def open_positions_returns(self, lookback: str = None, date: datetime = None) -> pd.DataFrame:
        """
        """
