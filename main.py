from datetime import datetime
from portfolio import Portfolio


ptf = Portfolio(account='tfsa')
ptf.fetch_prices(read=True)

print('')
