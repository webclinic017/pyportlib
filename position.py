import pandas as pd


class Position(object):

    def __init__(self,
                 ticker: str):
        self.ticker = ticker

    def __repr__(self):
        return f"{self.ticker} - Equity"
