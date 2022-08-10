from datetime import datetime

from pyportlib.utils import dates_utils


class TestDates:

    def test_lastbday_us(self):
        day = dates_utils.last_bday(as_of=datetime(2022, 5, 23))

        assert day == datetime(2022, 5, 23)

    def test_lastbday_can(self):
        day = dates_utils.last_bday(as_of=datetime(2022, 5, 23), calendar="TSX")

        assert day == datetime(2022, 5, 20)

    def test_lastbday_on_bday(self):
        day = dates_utils.last_bday(as_of=datetime(2022, 5, 20))

        assert day == datetime(2022, 5, 20)

    def test_datewindow(self):
        window = dates_utils.date_window('1y', datetime(2022, 1, 1))

        assert window == datetime(2020, 12, 31)
