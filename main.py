from datetime import datetime

from portfolio import Portfolio
import quantstats as qs
qs.extend_pandas()


ptf = Portfolio(account='tfsa', load_data=True)
print(ptf.cash())
print(ptf.dividends())

print('')


