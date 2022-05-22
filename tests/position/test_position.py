from datetime import datetime

import pyportlib


class TestPosition:
    date = datetime(2022, 5, 20)

    def test_get_price(self):
        pos = pyportlib.Position("AAPL", "USD")

        assert pos
        assert round(pos.prices.loc[self.date], 4) == 137.59


