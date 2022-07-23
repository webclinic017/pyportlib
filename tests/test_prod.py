import pyportlib


class TestProd:
    def test_create_large_ptf(self):
        ptf = pyportlib.create.portfolio("questrade_tfsa", "CAD")

        assert ptf
