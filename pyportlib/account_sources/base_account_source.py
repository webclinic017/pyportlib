from datetime import datetime
from typing import List

from ..portfolio import Portfolio


class BaseAccountSource:

    def get_positions(self):
        raise NotImplementedError()

    def get_balances(self):
        raise NotImplementedError()

    def get_transactions(self, start_date: datetime = None, end_date: datetime = None) -> List[dict]:
        raise NotImplementedError()

    def update_ptf(self, portfolio: Portfolio, start_date: datetime = None) -> None:
        raise NotImplementedError()