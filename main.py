from datetime import datetime
from portfolio import Portfolio
from transaction import Transaction

ptf = Portfolio(account='tfsa', load_data=True)
ptf.get_market_value()
print('')
