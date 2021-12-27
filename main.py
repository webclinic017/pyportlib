from datetime import datetime
import quantstats as qs
from portfolio import Portfolio
import utils.timing as timing
from reports import portfolio_reports

ptf = Portfolio(account='tfsa', currency="CAD")
timing.midlog("loading")

x = ptf.daily_unrealized_pnl_pct(start_date=ptf.start_date)
portfolio_reports.report(x, "XIU.TO", name="test")

print('')


