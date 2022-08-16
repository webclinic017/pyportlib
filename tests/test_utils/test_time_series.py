from datetime import datetime

import pandas as pd
from freezegun import freeze_time

from pyportlib import create
from pyportlib.utils.time_series import remove_leading_zeroes, remove_consecutive_zeroes, prep_returns


class TestTimeSeries:

    def test_remove_leading_zeroes(self):
        s = pd.Series(data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1])

        result = remove_leading_zeroes(s)

        assert result[13] == 0
        assert result[14] == 0
        assert result[15] == 0
        assert result.iloc[0] != 0

    def test_remove_consecutive_zeroes(self):
        s = pd.Series(data=[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1])

        result = remove_consecutive_zeroes(s)

        assert result.iloc[0] != 0
        assert result[15] == 0
        assert result.iloc[-1] == 1

    def test_prep_returns_start_date_only(self):
        date = datetime(2021, 1, 1)
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, start_date=date)

        assert result.index[0] == datetime(2020, 12, 31)

    def test_prep_returns_end_date_only(self):
        date = datetime(2021, 1, 1)
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, end_date=date)

        assert result.index[0] == datetime(2019, 12, 31)

    def test_prep_returns_end_date_and_lookback(self):
        date = datetime(2021, 1, 1)
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, end_date=date, lookback='1y')

        assert result.index[0] == datetime(2019, 12, 31)

    def test_prep_returns_end_date_and_start_date_and_lookback(self):
        date = datetime(2021, 1, 1)
        date1 = datetime(2000, 1, 1)
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, start_date=date1, end_date=date, lookback='1y')

        assert result.index[0] == datetime(2019, 12, 31)

    def test_prep_returns_end_date_and_start_date(self):
        date = datetime(2021, 1, 1)
        date1 = datetime(2006, 12, 29)
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, start_date=date1, end_date=date)

        assert result.index[0] == date1

    @freeze_time('2022-08-15')
    def test_prep_returns_only_lookback(self):
        pos = create.position("AAPL", "USD", "")
        result = prep_returns(ts=pos.prices, lookback='1y')

        assert result.index[-1] == datetime(2022, 8, 12)
        assert result.index[0] == datetime(2021, 8, 12)
