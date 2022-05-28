# Pyportlib
Author: Philippe Lacroix-Ouellete, HEC Montréal. (philippe.lacroix.ouellette@gmail.com)

Firstly, this package manages a stock prices/statements within a set directory, and so, 
directly from import. To override the default directory, use *set_client_dir(str)* in your script. 
You can build equity portfolios and compute its historical 
performances, including intraday transactions PnL. Some key metrics can also be computed (see */reporting/* and */metrics/stats.py*).

On the other hand, you can leverage the *Position* object to retreive and manipulate stock data with quantities. 
It is then possible to compute its daily performance and statistics obviously for research purposes. Financial statements can also be retreived.

- Construct portfolios with transactions
    - Track cash changes within the portfolio and cash account on any given date.
    - Transaction can be entered through the Transaction object within the code or a transaction.csv within the portoflio directory
    - Transactions and Cash changes can be updated through the questrade connection. See below.
    - Compute daily PnL in $ or % and compute other key risk metrics, by position tags.

- Generate a tearsheat from portoflio performance, plots, etc.
    - Compute strategy performance
    - Build custom and dynamic benchmarks etc.

Most of the stats and plots modules wrap around quantstats package. Currently has yahoo as implemented source (yfinance and yahoo_fin)

See */examples/* and */tests/*

## Questrade Connection
Update your portfolio with the questrade connection. 
Retreive account information and transactions and *QuestradeConnection* can manage 
all of your portfolio changes firectly from your account.

Example is available in */examples/questrade*.

## Other
Package also offers utility functions useful for any quantitative/analytics research workflow such as 
indices symbols, calendar management and rolling date ranges.

## Future Plans
 - Facilitating what-if scenarios, with temporary positions that do not persist in your actual account transaction. Instead of creating a new portfolio everytime.