from datetime import datetime

import pyportlib


class TestStats:
    p = pyportlib.Portfolio(account="Testing", currency="CAD")
    start = datetime(2022, 1, 1)
    date = datetime(2022, 5, 12)
    split_date = datetime(2022, 5, 20)

    def setup_ptf(self):
        self.p.reset()
        self.p.add_cash_change(cash_changes=pyportlib.CashChange(self.start, "Deposit", 1000000.))
        trx = pyportlib.Transaction(self.date,
                                    "AAPL",
                                    "Buy",
                                    10,
                                    100,
                                    0,
                                    "USD")
        self.p.add_transaction(trx)

    def test_pnl(self):
        self.setup_ptf()
        var = pyportlib.stats.skew(self.p, lookback='1y')
