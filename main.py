from portfolio import Portfolio

ptf = Portfolio(account='tfsa')
# ptf.load_prices(read=True)
ptf.transaction_manager.compute_wac()


print('')
