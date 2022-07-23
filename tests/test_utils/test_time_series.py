import pandas as pd

from pyportlib.utils.time_series import remove_leading_zeroes, remove_consecutive_zeroes


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
