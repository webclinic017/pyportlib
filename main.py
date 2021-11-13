from datetime import datetime
from portfolio import Portfolio
from transaction import Transaction

ptf = Portfolio(account='tfsa')

trx = Transaction(date='2021-10-10',
                  ticker='AAPL',
                  type='Sell',
                  quantity=-2,
                  price=350.0,
                  fees=5,
                  currency='USD')
ptf.transaction_manager.add(trx)

print(ptf.transaction_manager.total_fees())

print('stop')