from datetime import datetime

from data_sources.alphavantage_connection import AlphaVantageConnection
from position import Position
from transaction_manager import TransactionManager
from utils.config_utils import fetch_data_sources


class Portfolio(object):

    def __init__(self, account: str):

        self.account = account
        self.transaction_manager = TransactionManager(account=self.account)
        self.positions = {}
        self.load_positions()

    def __repr__(self):
        return self.account

    def get_position(self, ticker):
        return self.positions.get(ticker)

    def load_positions(self):
        tickers = self.transaction_manager.live_tickers()
        for ticker in tickers:
            self.positions[ticker] = Position(ticker)
        print(f'positions for {self.account} loaded')

    def fetch_prices(self, read: bool):
        start = datetime(1900, 1, 1)
        end = datetime.today()
        for pos in self.positions.keys():
            self.get_position(pos).fetch_prices(start, end, read=read)

