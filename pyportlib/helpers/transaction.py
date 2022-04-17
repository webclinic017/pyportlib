from datetime import datetime
import pandas as pd
from ..utils import logger


class Transaction:
    _NAME = 'Transaction'
    _INFO = ['Date', 'Ticker', 'Type', 'Quantity', 'Price', 'Fees', 'Currency']
    _TYPES = ["Buy", "Sell", "Dividend"]

    def __init__(self,
                 date: datetime,
                 ticker: str,
                 transaction_type: str,
                 quantity: int,
                 price: float,
                 fees: float,
                 currency: str):

        self.date = date
        self.ticker = ticker.upper()
        self.type = transaction_type.title()
        self.quantity = quantity
        self.price = price
        self.fees = fees
        self.currency = currency
        self.check()

    def __repr__(self):
        return f"{self._NAME} - {self.date.date()} - {self.type} - {self.ticker}"

    @property
    def df(self) -> pd.DataFrame:
        """
        Pandas DataFrame representation of the Transaction
        :return:
        """
        columns = ['Ticker', 'Type', 'Quantity', 'Price', 'Fees', 'Currency']
        data = [self.ticker, self.type, self.quantity, self.price, self.fees, self.currency]
        new = pd.DataFrame(index=[self.date], columns=columns)
        new.loc[self.date] = data
        new.index.name = 'Date'

        return new

    @property
    def info(self):
        return {'Ticker': self.ticker,
                'Type': self.type,
                'Quantity': self.quantity,
                'Price': self.price,
                'Fees': self.fees,
                'Currency': self.currency}

    def check(self) -> None:
        """
        Checks if transaction object is valid
        :return:
        """
        condition1 = self.type in self._TYPES
        # currencies = ['USD', 'CAD']
        # condition2 = self.currency in currencies
        condition3 = isinstance(self.date, datetime)
        condition4 = (self.quantity > 0 and self.type == 'Buy') or (self.quantity == 0 and self.type == 'Dividend') or (self.quantity < 0 and self.type == 'Sell')

        if not condition1:
            logger.logging.error(f'transaction type {self.type} is invalid, must be in {self._TYPES}')
            print(self.df)
        # if not condition2:
        #     logger.logging.error(f'transaction currency {self.type} is invalid, must be in {currencies}')
        #     print(self.df)
        if not condition3:
            logger.logging.error(f'transaction date {self.date} is invalid, must be datetime')
            print(self.df)
        if not condition4:
            logger.logging.error(f'transaction type {self.type} and quantity {self.quantity} are invalid')
            print(self.df)
