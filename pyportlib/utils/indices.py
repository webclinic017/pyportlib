import pandas as pd


class SP500:
    def __repr__(self):
        return 'S&P 500 Index'

    @staticmethod
    def _sp500():
        df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        df = df[['Symbol', 'GICS Sector']]
        df.rename(columns={'Symbol': 'Ticker', 'GICS Sector': 'Sector'}, inplace=True)
        return df

    @property
    def constituents(self):
        return self._sp500()['Ticker'].to_list()


class NASDAQ100:
    def __repr__(self):
        return 'NASDAQ 100 Index'

    @staticmethod
    def _nasdaq100():
        df = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[3]
        df = df[['Ticker', 'GICS Sector']]
        df.rename(columns={'GICS Sector': 'Sector'}, inplace=True)
        return df

    @property
    def constituents(self):
        return self._nasdaq100()['Ticker'].to_list()
