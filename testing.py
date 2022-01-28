import portofolio as porto
import logging

logging.getLogger().setLevel(logging.ERROR)

ptf = porto.Portfolio(account='tfsa', currency="CAD")

# Transactions
print(ptf.transactions.head())

# with the data that is currently loaded
pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date)
