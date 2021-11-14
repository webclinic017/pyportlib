from datetime import datetime
from position import Position
from transaction_manager import TransactionManager
import pandas as pd


class Portfolio(object):

    def __init__(self, account: str):

        self.account = account
        self.transaction_manager = TransactionManager(account=self.account)
        self.positions = {}
        self.load_positions()
        self.prices_df = pd.DataFrame()

    def __repr__(self):
        return self.account

    def get_position(self, ticker):
        return self.positions.get(ticker)

    def load_positions(self):
        tickers = self.transaction_manager.all_tickers()
        for ticker in tickers:
            currency = 'CAD' if ticker[-4:] == '.TRT' else 'USD'
            self.positions[ticker] = Position(ticker, currency=currency)
        print(f'positions for {self.account} loaded')

    def load_prices(self, read: bool):
        start = datetime(1900, 1, 1)
        end = datetime.today()
        for pos in self.positions.keys():
            self.get_position(pos).load_prices_local(start, end, read=read)
            self.get_position(pos).load_prices_cad(start, end, read=read)
        self.load_prices_df()

    def load_prices_df(self):
        if self.prices_df.empty:
            df = self.positions[list(self.positions.keys())[0]].load_prices_cad()
            df.columns = [list(self.positions.keys())[0]]
            # TODO fix this
            for position in list(self.positions.values())[1:]:
                prices = position.load_prices_cad()
                prices.columns = [position.ticker]
                df = pd.merge(df, prices, how='outer', on='Date')
            self.prices_df = df.dropna(how='all').sort_index()
            print(f'most recent data point: {self.prices_df.index.max()}')
        return self.prices_df

