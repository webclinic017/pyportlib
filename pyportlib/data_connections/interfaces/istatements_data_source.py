from abc import ABC, abstractmethod


class IStatementsDataSource(ABC):

    @abstractmethod
    def get_balance_sheet(self, ticker: str):
        """
        """

    @abstractmethod
    def get_cash_flow(self, ticker: str):
        """
        """

    @abstractmethod
    def get_income_statement(self, ticker: str):
        """
        """

    @abstractmethod
    def get_dividends(self, ticker: str, start_date=None, end_date=None):
        """
        """
