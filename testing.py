import portofolio as porto
import logging

ptf = porto.Portfolio(account='tfsa', currency="CAD")
print(ptf.transactions.head())

aapl = porto.Position(ticker='AAPL', currency='USD')

print(aapl.daily_pnl())