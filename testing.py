from datetime import datetime

import portofolio as porto

portfolio = porto.Portfolio(account='Example', currency="CAD")
portfolio.reset()

print(portfolio.transactions)
print(portfolio.cash_history)
print(portfolio)

portfolio.add_cash_change(date=datetime(2022, 1, 1), direction="Deposit", amount=1_000_000)

transaction = porto.Transaction(date=datetime(2022, 1, 31),
                                ticker="AAPL",
                                type="Buy",
                                quantity=10,
                                price=160.,
                                fees=5.,
                                currency="USD")

portfolio.add_transaction([transaction])

print(portfolio.positions.get('AAPL').quantities)

portfolio.update_data()

portfolio.reset()
print('')