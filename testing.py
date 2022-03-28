import pyportlib
from datetime import datetime

ptf = pyportlib.Portfolio(account='questrade_tfsa', currency="CAD")
benchmark = pyportlib.Portfolio(account='bench_tfsa', currency='CAD')

# q = QuestradeConnection(account_name='tfsa')
# q.update_transactions(portfolio=ptf, start_date=datetime(2019, 5, 1))

lk = "5y"
rolling_alpha = pyportlib.stats.rolling_alpha(ptf, lookback=lk, benchmark=benchmark, rolling_period=5, include_cash=True)
pyportlib.plots.returns(rolling_alpha, lookback=lk, compound=False)
pyportlib.plots.returns(ptf, lookback=lk, benchmark=benchmark,include_cash=True)
print("")