from datetime import datetime
import quantstats as qs

from data_sources.data_reader import DataReader
from portfolio import Portfolio
import utils.timing as timing
from reports import portfolio_reports

ptf = Portfolio(account='tfsa', currency="CAD")
# ptf.update_data()
timing.midlog("loading")

x = ptf.daily_unrealized_pnl_pct(start_date=ptf.start_date)

portfolio_reports.report(x, "SPY", name="tfsa_2022-01-19", rf=0.)

print('')
