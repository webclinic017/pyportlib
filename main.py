from datetime import datetime
from portfolio import Portfolio
from transaction import Transaction

ptf = Portfolio(account='test', load_data=True)
trx = Transaction(ticker='HTGC',
                  date=datetime(2021, 11, 17),
                  type='Buy',
                  quantity=100,
                  price=18.,
                  fees=5,
                  currency='USD')

ptf.add_transaction(trx)
print('')
