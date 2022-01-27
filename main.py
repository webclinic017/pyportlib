from datetime import datetime

from portfolio import Portfolio
import utils.timing as timing
from reporting import reporting
from transaction import Transaction

ptf = Portfolio(account='TEST111', currency="CAD")

# ptf.add_cash_change(date=datetime(2022, 1, 1), direction="Deposit", amount=1000000000000)
transaction = Transaction(date=datetime(2022, 1, 7),
                          ticker='VOO',
                          type='Buy',
                          quantity=2,
                          price=395,
                          fees=0,
                          currency='USD')
ptf.add_transaction([transaction])

pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date).iloc[1:]
timing.midlog("pnl compute")

date = datetime.today()
reporting.full_html(pnl, "SPY", name=f"tfsa_{date.date()}", rf=0.)

print('')
