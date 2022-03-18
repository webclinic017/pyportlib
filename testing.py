import pyportlib

x = pyportlib.Portfolio(account='questrade_tfsa', currency="CAD")
pyportlib.stats.rolling_var(x, lookback='1y')