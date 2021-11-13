from portfolio import Portfolio
from transaction import Transaction


def add_transactions(account: str):
    add = True

    while add:
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

        add = input("Add another transaction? (True/False): ")


