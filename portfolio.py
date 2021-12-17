from datetime import datetime
from typing import List, Union
from cash_account import CashAccount
from data_sources.data_reader import DataReader
from fx_rates import FxRates
from position import Position
from transaction import Transaction
from transaction_manager import TransactionManager
from utils import logger, dates_utils
import pandas as pd


class Portfolio(object):

    def __init__(self, account: str, currency: str):
        # attributes
        self.account = account
        self.positions = {}
        self.currency = currency
        self.prices = pd.DataFrame()
        self.quantities = pd.DataFrame()
        self.market_value = pd.DataFrame()
        
        # helpers
        self.cash_account = CashAccount(account=self.account)
        self.datareader = DataReader()
        self.transaction_manager = TransactionManager(account=self.account)
        self.fx = FxRates(ptf_currency=currency, currencies=self.transaction_manager.get_currencies())

        self.start_date = self.transaction_manager.first_trx_date()
        # load data        
        self.load_data()

    def __repr__(self):
        return self.account

    def load_data(self) -> None:
        self.transaction_manager.fetch()
        self._load_positions()
        # self._load_prices() # TODO fx
        self._load_quantities()
        # self._load_market_value() # TODO fx
        logger.logging.info(f'{self.account} data loaded')

    def update_data(self) -> None:
        self._refresh_prices()
        self._refresh_fx()
        self.load_data()
        self.transaction_manager.fetch()
        logger.logging.info(f'{self.account} refreshed')

    def _refresh_fx(self) -> None:
        self.fx.refresh()

    def _refresh_prices(self) -> None:
        for ticker in self.positions.keys():
            self.datareader.update_prices(ticker=ticker)

    def _get_fx(self, currency):
        pair = f"{currency}{self.currency}"
        return self.fx.get(pair)

    def _load_market_value(self) -> None:  # FIXME make for a specific date, not a time series
        if len(self.positions):
            last_date = self.datareader.last_data_point(self.account)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            market_value = pd.Series(index=dates, data=[0 for _ in range(len(dates))])

            for position in self.positions.values():
                if self.currency == position.currency:
                    pos_val = self.quantities[position.ticker] * position.get_prices().iloc[:, 0]
                else:
                    fx = self.fx.get(position.currency)
                    pos_val = self.quantities[position.ticker] * position.get_prices().iloc[:, 0] * fx

                pos_val = pos_val.fillna(method='ffill')
                market_value += pos_val
                market_value = market_value.fillna(method='ffill')
            self.market_value = market_value
            logger.logging.info(f'{self.account} market_value computed')
        else:
            logger.logging.info(f"{self.account} no positions in portfolio")

    def get_market_value(self):
        return self.market_value

    def _load_positions(self,) -> None:
        tickers = self.transaction_manager.live_positions()
        for ticker in tickers:
            currency = self.transaction_manager.get_currency(ticker=ticker)
            pos = Position(ticker, currency=currency, ptf_currency=self.currency, datareader=self.datareader)
            self.positions[ticker] = pos
        logger.logging.info(f'positions for {self.account} loaded')

    def get_position(self, ticker: str = None) -> Union[Position, dict]:
        if ticker:
            return self.positions.get(ticker)
        else:
            return self.positions

    def _load_prices(self) -> None:  # FIXME FXXXXX 
        pos = list(self.get_position().values())
        if len(pos):
            self.prices = self._make_prices_df(pos, start_date=self.start_date)

            logger.logging.info(f'{self.account} position prices loaded')
        else:
            logger.logging.info(
                f'{self.account} no positions in portfolio')

    def get_prices(self):
        return self.prices

    def _load_quantities(self) -> None:
        if len(self.positions):
            self.quantities = pd.DataFrame()
            last_date = self.datareader.last_data_point(account=self.account)
            dates = dates_utils.get_market_days(start=self.start_date, end=last_date)
            self.quantities.index = dates

            for position in self.positions.values():
                trx = self.transaction_manager.transactions.loc[(self.transaction_manager.transactions.Ticker == position.ticker)
                                                                & (self.transaction_manager.transactions.Type != 'Dividend')]
                self.quantities[position.ticker] = trx['Quantity']
                logger.logging.debug(f'quantities computed for {position}')

            self.quantities = self.quantities.fillna(0).cumsum()

        else:
            logger.logging.info(f'{self.account} no positions in portfolio')

    def get_quantities(self):
        return self.quantities

    def add_transaction(self, transaction: Transaction) -> None:
        value = transaction.quantity * transaction.price
        pair = f"{transaction.currency}{self.currency}"
        if not len(self.fx.get(transaction.currency)):

            self.fx[transaction.currency] = self.datareader.read_fx(currency_pair=pair)

        if transaction.currency != self.currency:
            value = (value * self.fx.get(transaction.currency).loc[transaction.date] + transaction.fees).iloc[0]
        live_cash = self.cash(date=transaction.date)
        new_cash = live_cash - value
        if value > live_cash:
            logger.logging.error(f'Not enough funds to perform this transaction, missing {-1 * new_cash} to complete')
        else:
            self.transaction_manager.add(transaction=transaction)

    def cash(self, date: datetime = None):  # FIXME for new fx module
        if date is None:
            date = self.datareader.last_data_point(account=self.account)

        live_fx = self.fx.get('USD').loc[date].iloc[0]
        changes = self.cash_account.get_cash_change(date)

        transactions = self.transaction_manager.get_transactions().loc[self.transaction_manager.get_transactions().index <= date, ]
        transactions.loc[:, 'Value'] = transactions.Quantity*transactions.Price
        transactions.loc[transactions.Currency == 'USD', 'Value'] *= live_fx
        values = transactions['Value'].sum()*-1

        dividends = self.dividends(end_date=date)

        return values+changes+dividends

    def dividends(self, start_date: datetime = None, end_date: datetime = None):  # FIXME for new fx module
        if len(self.positions):
            if end_date is None:
                end_date = self.datareader.last_data_point(account=self.account)
            if start_date is None:
                start_date = self.start_date
            live_fx = self.fx.get('USD').loc[end_date].iloc[0]
            transactions = self.transaction_manager.get_transactions().loc[(self.transaction_manager.get_transactions().index <= end_date) & (self.transaction_manager.get_transactions().index >= start_date), ]
            dividends = transactions.loc[transactions.Type == 'Dividend', ['Price', 'Currency']]
            dividends.loc[dividends.Currency == 'USD', 'Price'] *= live_fx
            return dividends['Price'].sum()
        else:
            return 0

    @staticmethod
    def _make_prices_df(positions: List[Position], start_date: datetime = None):

        df = positions[0].get_prices().loc[start_date:]
        df.columns = [positions[0].ticker]

        for pos in positions[1:]:
            prices = pos.get_prices().loc[start_date:]
            prices.columns = [pos.ticker]
            df = pd.concat([df, prices], axis=1)
        return df.dropna(how='all').sort_index()
