from datetime import datetime

from portfolio import Portfolio
import utils.timing as timing
from reporting import reporting

ptf = Portfolio(account='tfsa', currency="CAD")
ptf.update_data()
timing.midlog("loading")
pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date).iloc[1:]
timing.midlog("pnl compute")

date = datetime.today()
reporting.full_html(pnl, "SPY", name=f"tfsa_{date.date()}", rf=0.)

print('')
