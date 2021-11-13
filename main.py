from datetime import datetime

from data_sources.alphavantage_connection import AlphaVantageConnection
from portfolio import Portfolio
from data_sources.simfin_connection import SimFinConnection

ptf = Portfolio(account='tfsa')

conn1 = AlphaVantageConnection()
conn2 = SimFinConnection()

start = datetime(2021, 10, 1)
end = datetime.today()
conn1.get_prices('AAPL', start=start, end=end)
conn2.get_prices('AAPL', start=start, end=end)