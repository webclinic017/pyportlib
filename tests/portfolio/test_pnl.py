from datetime import datetime

import pyportlib


class TestPnl:
    p = pyportlib.create.portfolio(account="Testing", currency="CAD")
    start = datetime(2022, 1, 1)
    date = datetime(2022, 5, 12)
    split_date = datetime(2022, 5, 20)

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

    def test_pnl(self):
        self.setup_ptf()
        pnl = self.p.daily_total_pnl(end_date=datetime(2022, 5, 17))

        assert round(pnl["AAPL"].item(), 6) == 39.249387
