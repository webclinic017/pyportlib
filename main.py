from portfolio import Portfolio

ptf = Portfolio(account='tfsa', cash=0, load_data=True)
ptf.load_prices_df()

print('')
