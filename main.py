from portfolio import Portfolio
import quantstats as qs
qs.extend_pandas()

ptf = Portfolio(account='tfsa', currency="CAD")
ptf.update_data()
print('')


