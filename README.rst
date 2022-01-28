# PortoFolio

Python package used to build equity portfolios based on transaction data. 
Built around yfinance API, but more data sources can be implemented.

Package/Project uses and structure is entirely designed based on my needs. quantstats is also leveraged.

###  Planned Functionalities
    - Performance tracking
    - Portfolio analytics
    - Quantitative research
    - Portfolio Construction
    - Optimisation
    - Backtesting

.. code:: python
    import portofolio as porto
    import quantstats as qs

    ptf = porto.Portfolio(account='tfsa', currency="CAD")

    # Transactions
    print(ptf.transactions.head())

    # with the data that is currently loaded
    pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date)
    qs.plots.snapshot(pnl)

.. code:: python
    from datetime import datetime

    # we can generate full html reports
    ptf = porto.Portfolio(account='tfsa', currency="CAD")
    ptf.update_data()
    pnl = ptf.pct_daily_total_pnl(start_date=ptf.start_date).iloc[1:]
    porto.reporting.full_html(pnl, "SPY", name=f"tfsa_{datetime.today().date()}", rf=0.)
    

