from datetime import datetime
from portfolio import Portfolio
import matplotlib.pyplot as plt

start = datetime(2020, 1, 1)
end = datetime(2021, 10, 10)

ptf = Portfolio(account='tfsa')
ptf.load_prices(read=True)

print('')
