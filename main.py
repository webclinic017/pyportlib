from portfolio import Portfolio

ptf = Portfolio(account='tfsa', load_data=True)
ptf.load_prices_df()

print('')
