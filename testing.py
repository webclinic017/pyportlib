from datetime import datetime
import portofolio as porto

ptf = porto.Portfolio(account='tfsa', currency="CAD")


porto.reporting.full_html(ptf, "SPY", name=f"{ptf.account}_{datetime.today().date()}", rf=0.)
