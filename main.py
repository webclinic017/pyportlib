from datetime import datetime
from portfolio import Portfolio
from transaction import Transaction

ptf = Portfolio(account='tfsa')

trx = Transaction(date=datetime(2021, 10, 10),
                  ticker='AAPL',
                  type='Sell',
                  quantity=-2,
                  price=350.0,
                  fees=5,
                  currency='USD')


print(ptf.transaction_service.total_fees())

print('stop')