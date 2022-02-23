import portofolio as porto

ticker = "CM.TO"
pos = porto.Position(ticker, local_currency="CAD")
pos.update_prices()


print(pos.prices.iloc[-1])