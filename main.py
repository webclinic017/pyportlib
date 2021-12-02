from datetime import datetime
from portfolio import Portfolio
from transaction import Transaction
import quantstats as qs
qs.extend_pandas()


ptf = Portfolio(account='tfsa', load_data=True)

print('')


