from datetime import datetime

from data_sources.data_reader import DataReader
from portfolio import Portfolio
from transaction import Transaction
import quantstats as qs
qs.extend_pandas()

ptf = Portfolio(account='tfsa', load_data=False)
ptf.refresh_all()

aapl = DataReader().read_prices('MSFT').sort_index().iloc[:, -1].loc[datetime(2014, 1, 1):]
stock = aapl.pct_change()
qs.reports.html(stock, title='', output='client_data/outputs/plot.html')


