# Pyportlib

Firstly, this package manages a stock prices/statements within a set directory, and so, directly from import. You can build long-only equity portfolios and compute its historical performances along with some key metrics (see *reporting.py*).

On the other hand, you can leverage the *Position* object to retreive and manipulate stock data with quantities. It is then possible to compute its daily performance and statistics obviously.

    - Construct portfolios with transactions
        - Track cash changes within the portfolio and cash account on any given date.
        - Transaction can be entered through the Transaction object within the code or a transaction.csv within the portoflio directory
        - Compute daily pnl in $ or % and compute other key risk metrics.
    
    - Generate a tearsheat from portoflio performance, plots, etc.
        - Compute strategy performance
        - Build custom and dynamic benchmarks etc.

Most of the stats and plots modules wrap around quantstats package.

See examples/examples.ipynb