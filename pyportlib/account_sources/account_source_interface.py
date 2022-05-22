from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from ..portfolio import Portfolio


class AccountSourceInterface(ABC):

    @abstractmethod
    def get_positions(self):
        raise NotImplementedError()

    @abstractmethod
    def get_balances(self):
        raise NotImplementedError()

    @abstractmethod
    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[dict]:
        raise NotImplementedError()

    @abstractmethod
    def update_ptf(self, portfolio: Portfolio, start_date: datetime = None) -> None:
        raise NotImplementedError()