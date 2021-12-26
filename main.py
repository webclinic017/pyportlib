from portfolio import Portfolio
import utils.timing as timing

ptf = Portfolio(account='tfsa', currency="CAD")
timing.midlog("ptf loaded")
c = ptf.get_position("SCYX").daily_price_diff()
timing.midlog("pnl")

print('')


