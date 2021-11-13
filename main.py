from datetime import datetime

from data_sources.alphavantage_connection import AlphaVantageConnection
from portfolio import Portfolio

start = datetime(2020, 1, 1)
end = datetime(2021, 10, 10)

ptf = Portfolio(account='tfsa')
ptf.load_prices(read=True)

print('')
