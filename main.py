from datetime import datetime

from portfolio import Portfolio

ptf = Portfolio(account='tfsa')
htgc = ptf.get_position('HTGC')
htgc.get_prices(start_date=datetime(2021, 11, 1))

print('')
