from datetime import datetime
from transaction import Transaction
from portfolio import Portfolio
import quantstats as qs
qs.extend_pandas()


ptf = Portfolio(account='test', load_data=True)
# trx = Transaction(date=datetime(2021, 12, 16),
#                   ticker='AAPL',
#                   type='Sell',
#                   quantity=-5,
#                   price=120.0,
#                   fees=5.,
#                   currency='USD')
#
# ptf.add_transaction(trx)
ptf.cash()
print('')


