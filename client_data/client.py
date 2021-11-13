from portfolio import Portfolio
from transaction import Transaction


def add_transaction(account: str):
    date = input('Date: ')
    ticker = input('Ticker: ')
    type = input('Type: ')
    quantity = int(input('Quantity: '))
    price = float(input('Price: '))
    fees = float(input('Fees: '))
    currency = input('Currency: ')
    trx = Transaction(date, ticker, type, quantity, price, fees, currency)

    ptf = Portfolio(account=account)
    ptf.transaction_manager.add(trx)


