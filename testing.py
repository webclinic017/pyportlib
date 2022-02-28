import portofolio as porto

p = porto.Position("AAPL", "USD")
print(p._datareader.read_dividends(p.ticker).iloc[-1])
print("")