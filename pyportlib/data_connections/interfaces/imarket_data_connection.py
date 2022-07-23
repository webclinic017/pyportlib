from abc import ABC, abstractmethod


class IMarketDataSource(ABC):

    @abstractmethod
    def get_prices(self, ticker: str) -> None:
        """
        """

    @abstractmethod
    def get_fx(self, currency_pair: str) -> None:
        """
        """

    @abstractmethod
    def get_splits(self, ticker: str):
        """
        """
