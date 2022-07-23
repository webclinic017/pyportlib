from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd


class IPosition(ABC):
    ticker: str
    currency: str

    @property
    @abstractmethod
    def tag(self):
        """
        """

    @tag.setter
    @abstractmethod
    def tag(self, value: str):
        """
        """

    @abstractmethod
    def update_data(self, fundamentals_and_dividends: bool = False) -> None:
        """
        """

    @abstractmethod
    def get_fundamentals(self, statement_type: str) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def get_splits(self) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def dividends(self) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def npv(self) -> pd.Series:
        """
        """


    @property
    @abstractmethod
    def prices(self) -> pd.Series:
        """
        """

    @prices.setter
    @abstractmethod
    def prices(self, prices: pd.Series) -> None:
        """
        """

    @property
    @abstractmethod
    def quantities(self) -> pd.Series:
        """
        """

    @quantities.setter
    @abstractmethod
    def quantities(self, quantities: pd.Series) -> None:
        """
        """

    @abstractmethod
    def daily_pnl(self,
                  start_date: datetime = None,
                  end_date: datetime = None,
                  transactions: pd.DataFrame = pd.DataFrame(),
                  fx: dict = None) -> pd.DataFrame:
        """
        """

    @abstractmethod
    def daily_total_pnl(self,
                        start_date: datetime = None,
                        end_date: datetime = None,
                        transactions: pd.DataFrame = pd.DataFrame(),
                        fx: dict = None) -> pd.DataFrame:
        """
        """
