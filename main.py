from portfolio import Portfolio
import utils.timing as timing
from reporting import reporting

ptf = Portfolio(account='tfsa', currency="CAD")
# ptf.update_data()
timing.midlog("loading")
print(ptf.cash())
timing.midlog("cash compute")

pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date).iloc[1:]
timing.midlog("pnl compute")

reporting.full_html(pnl, "SPY", name="tfsa_jan25-2022", rf=0.)

print('')
