from datetime import datetime

import pyportlib


class TestStats:
    p = pyportlib.create.portfolio(account="Testing", currency="CAD")
    start = datetime(2022, 1, 1)
    date = datetime(2022, 5, 12)
    end_date = datetime(2022, 5, 20)

    def setup_ptf(self):
        self.p.reset()
        self.p.add_cash_change(cash_changes=pyportlib.create.cash_change(self.start, "Deposit", 1000000.))
        trx = pyportlib.create.transaction(self.date,
                                           "AAPL",
                                           "Buy",
                                           10,
                                           100,
                                           0,
                                           "USD")
        self.p.add_transaction(trx)

    def test_skew(self):
        self.setup_ptf()
        var = pyportlib.stats.skew(self.p, end_date=self.end_date, lookback='1y')

        assert round(var, 5) == 2.27105

    def test_weights_plot_no_error(self):
        pyportlib.plots.position_allocation(self.p, date=self.date)

    def test_strategy_weights_plot_no_error(self):
        pyportlib.plots.strategy_allocation(self.p, date=self.date)

    def test_weights_no_error_real_ptf(self):
        ptf = pyportlib.create.portfolio(account='questrade_tfsa', currency="CAD")
        ptf.position_weights()
        pyportlib.plots.position_allocation(ptf)
        pyportlib.plots.strategy_allocation(ptf)
