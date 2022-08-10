import pyportlib
from utils import dates_utils


class TestProd:
    def test_create_large_ptf(self):
        ptf = pyportlib.create.portfolio("questrade_tfsa", "CAD")

        assert ptf

    def test_pnl_large_ptf(self):
        ptf = pyportlib.create.portfolio("questrade_tfsa", "CAD")
        date = dates_utils.last_bday()
        ptf.pct_daily_total_pnl(end_date=date)
        assert ptf
