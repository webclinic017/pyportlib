from datetime import datetime

import pyportlib


class TestAddTransactions:
    p = pyportlib.create.portfolio(account="Testing", currency="CAD")
    start = datetime(2022, 1, 1)
    date = datetime(2022, 5, 12)
    split_date = datetime(2022, 5, 20)

    def setup_ptf(self):
        self.p.reset()
        self.p.add_cash_change(cash_changes=pyportlib.create.cash_change(self.start, "Deposit", 1000000.))

    def test_add_transaction(self):
        self.setup_ptf()
        trx = pyportlib.create.transaction(self.date,
                                           "AAPL",
                                           "Buy",
                                           10,
                                           100,
                                           0,
                                           "USD")
        self.p.add_transaction(trx)

        assert len(self.p.transactions) == 1
        assert self.p.transactions.loc[self.date, "Price"] == 100

    def test_add_split(self):
        self.setup_ptf()
        trx = pyportlib.create.transaction(self.date,
                                           "AAPL",
                                           "Buy",
                                           10,
                                           100,
                                           0,
                                           "USD")
        self.p.add_transaction(trx)

        split = pyportlib.create.transaction(self.split_date,
                                             "AAPL",
                                             "Split",
                                             0,
                                             2,
                                             0,
                                             "USD")
        self.p.add_transaction(split)

        assert self.p.transactions.loc[self.date, "Price"] == 50
        assert self.p.transactions.loc[self.split_date, "Type"] == "Split"
        assert self.p.transactions.loc[self.split_date, "Price"] == 2
