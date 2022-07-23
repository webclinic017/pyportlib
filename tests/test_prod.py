import pyportlib as p


class TestProd:

    def test_create_large_ptf(self):
        ptf = p.Portfolio("questrade_tfsa", "CAD")

        assert ptf
