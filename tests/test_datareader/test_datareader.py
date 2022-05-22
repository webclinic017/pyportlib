from datetime import datetime

from pyportlib.services.data_reader import DataReader


class TestDataReader:
    date = datetime(2022, 5, 20)
    dr = DataReader()

    def test_read_prices(self):
        prices = self.dr.read_prices("AAPL")

        assert not prices.empty
        assert round(prices.loc[self.date], 4) == 137.59

    def test_get_splits(self):
        splits = self.dr.get_splits("AAPL")

        assert not splits.empty
        assert splits.loc[datetime(2014, 6, 9)] == 7

    def test_fx(self):
        fx = self.dr.read_fx("USDUSD")

        assert not fx.empty
        assert fx.iloc[1] == 1



