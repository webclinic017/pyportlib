from enum import Enum
from typing import List
import pandas as pd


class Indexes(Enum):
    SP500 = "S&P 500"
    NASDAQ = "NASDAQ 100"


class Index:
    def __init__(self, index_name: str):
        self._index = Indexes[index_name.upper()]
        self.index_info = self.set_index(index=self._index)

    def set_index(self, index: Indexes):
        if index is Indexes.SP500:
            return self._sp()
        if index is Indexes.NASDAQ:
            return self._nasdaq()

    def __repr__(self):
        return self._index.value

    @staticmethod
    def _sp() -> pd.DataFrame:
        """
        Fetch the index constituents directly from the wikipedia page
        :return:
        """
        df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        df = df[['Symbol', 'GICS Sector']]
        df.rename(columns={'Symbol': 'Ticker', 'GICS Sector': 'Sector'}, inplace=True)
        return df

    @staticmethod
    def _nasdaq():
        """
        Fetch the index constituents directly from the wikipedia page
        :return:
        """
        df = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[3]
        df = df[['Ticker', 'GICS Sector']]
        df.rename(columns={'GICS Sector': 'Sector'}, inplace=True)
        return df

    @property
    def constituents(self) -> List[str]:
        """
        Get the index constituents
        :return:
        """
        return self.index_info['Ticker'].to_list()
