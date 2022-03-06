# Portofolio

Firstly, this package manages a stock prices/statements within your working directory, and so, directly from import. You can build long-only equity portfolios and compute its historical performances along with some key metrics (see *reporting.py*).

On the other hand, you can leverage de position object to retreive and manipulate stock data with quantities. It is then possible to compute its daily performance and statistics obviously.


    -Construct portfolios with transactions
        -Track cash changes within the portfolio and cash account on any given date.
        -Transaction can be entered through the Transaction object within the code or a transaction.csv within the portoflio directory
    -Generate a tearsheat from portoflio performance
        -Backtests
        -Build benchmarks etc.

See examples/examples.ipynb