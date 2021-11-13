from datetime import datetime
from portfolio import Portfolio


ptf = Portfolio(account='tfsa')

start = datetime(2021, 10, 1)
end = datetime(2021, 10, 5)

for pos in ptf.positions.keys():
    print(ptf.get_position(pos).fetch_prices(start, end, read=True))
    
pos = ptf.get_position('HTGC')
print('')
