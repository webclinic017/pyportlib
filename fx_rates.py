from datetime import datetime
from typing import List, Union

import pandas as pd

from data_sources.data_reader import DataReader
from utils import logger
from utils.dates_utils import get_market_days


class FxRates:
    def __init__(self, ptf_currency: str, currencies: List[str]):
        self.currencies = currencies
        self.rates = {}
        self.datareader = DataReader()
        self.ptf_currency = ptf_currency
        self._load()

    def set(self, currencies: List[str]):
        self.currencies = currencies
        self._load()

    def refresh(self):
        for curr in self.currencies:
            pair = f'{curr}{self.ptf_currency}'
            self.datareader.update_fx(currency_pair=pair)
        self._load()

    def get(self, currency: str):
        return self.rates.get(currency)

    def _load(self):
        for curr in self.currencies:
            pair = f'{curr}{self.ptf_currency}'
            if self.ptf_currency == curr:
                last_date = self.datareader.read_fx(currency_pair=pair).index.max()
                dates = get_market_days(start=datetime(2000, 1, 1), end=last_date)
                self.rates[curr] = pd.DataFrame(index=dates, columns=['Close'], data=[1 for _ in range(len(dates))])

            self.rates[curr] = self.datareader.read_fx(currency_pair=pair)
        logger.logging.info(f'fx rates loaded')

