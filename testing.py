import portofolio as porto
import logging

logging.getLogger().setLevel(logging.ERROR)

ptf = porto.Portfolio(account='tfsa', currency="CAD")

aapl = porto.Position(ticker='AAPL', currency='USD')

print(aapl.daily_pnl())