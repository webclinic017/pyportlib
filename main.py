from portfolio import Portfolio
import utils.timing as timing
from reports import portfolio_reports

ptf = Portfolio(account='tfsa', currency="CAD")
# ptf.update_data()
timing.midlog("loading")
print(ptf.cash())
x = ptf.daily_total_pnl_pct(start_date=ptf.start_date).iloc[1:]
timing.midlog("pnl compute")

portfolio_reports.report(x, "SPY", name="tfsa_jan24-2022", rf=0.)

print('')
