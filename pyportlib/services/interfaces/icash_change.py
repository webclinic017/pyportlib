from abc import ABC, abstractmethod


class ICashChange(ABC):

    @property
    @abstractmethod
    def info(self) -> dict:
        """
        """