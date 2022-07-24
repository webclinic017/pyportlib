from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd


class ITransaction(ABC):
    currency: str
    fees: float
    ticker: str
    date: datetime
    price: float
    quantity: int

    @property
    @abstractmethod
    def df(self) -> pd.DataFrame:
        """
        """

    @property
    @abstractmethod
    def info(self) -> dict:
        """
        """