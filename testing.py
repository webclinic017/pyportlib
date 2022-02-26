from datetime import datetime

import portofolio as porto

p = porto.Position("AAPL", "USD")
x = p.get_fundamentals('income_statement')

print('')