from datetime import datetime

from helpers.transaction import Transaction
from portfolio import Portfolio

new_ptf = Portfolio("TEST111", currency="USD")
print(new_ptf.transactions)
trx = Transaction(date=datetime(2022, 1, 27),
                  ticker="AAPL",
                  type="Buy",
                  quantity=10,
                  price=120.,
                  fees=0.,
                  currency="USD")

new_ptf.add_transaction([trx])
"with new transaction"
print(new_ptf.transactions)
