from pyportlib import Portfolio, QuestradeConnection
from datetime import datetime

ptf = Portfolio(account='questrade_tfsa', currency="CAD")
q = QuestradeConnection(account_name='tfsa')
q.update_transactions(portfolio=ptf, start_date=datetime(2019, 5, 1))
print("")