from datetime import datetime

from containers.datareader_container import DataReaderContainer
from utils import config_utils


class TestDataReader:
    date = datetime(2022, 5, 20)
    data_source_config = config_utils.data_source_config()

    datareader_container = DataReaderContainer(config=data_source_config)
    dr = datareader_container.datareader()

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



