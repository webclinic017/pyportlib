import pyportlib

x = pyportlib.Portfolio(account='questrade_tfsa', currency="CAD")
d = x._datareader.last_data_point(account=x.account, ptf_currency=x.currency)
x.open_positions(d)