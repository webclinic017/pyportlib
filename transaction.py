from datetime import datetime

import pandas as pd


class Transaction(object):
    TRANSACTIONS_INFO = ['Date', 'Ticker', 'Type', 'Quantity', 'Price', 'Fees', 'Currency']
    name = 'Transaction'

    def __init__(self,
                 date: str,
                 ticker: str,
                 type: str,
                 quantity: int,
                 price: float,
                 fees: float,
                 currency: str):

        self.date = date
        self.ticker = ticker.upper()
        self.type = type.title()
        self.quantity = quantity
        self.price = price
        self.fees = fees
        self.currency = currency

        self.check()

    def __repr__(self):
        return f"{self.name} {self.date} {self.ticker}"

    def get(self):
        columns = ['Ticker', 'Type', 'Quantity', 'Price', 'Fees', 'Currency']
        data = [self.ticker, self.type, self.quantity, self.price, self.fees, self.currency]
        new = pd.DataFrame(index=[self.date], columns=columns)
        new.loc[self.date] = data

        return new

    def check(self):
        types = ['Buy', 'Sell', 'Dividend']
        condition1 = self.type in types

        currencies = ['USD', 'CAD', 'EUR', 'GBP']
        condition2 = self.currency in currencies

        condition3 = len(self.date) == 10

        condition4 = (self.quantity > 0 and self.type == 'Buy') or (self.quantity == 0 and self.type == 'Dividend') or (self.quantity < 0 and self.type == 'Sell')

        if not condition1:
            raise ValueError(f'transaction type {self.type} is invalid, must be in {types}')
        if not condition2:
            raise ValueError(f'transaction currency {self.type} is invalid, must be in {currencies}')
        if not condition3:
            raise ValueError(f'transaction date {self.date} is invalid, must be in YYYY-mm-dd format')
        if not condition4:
            raise ValueError(f'transaction type {self.type} and quantity {self.quantity} are invalid')
