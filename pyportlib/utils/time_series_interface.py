from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union
import pandas as pd

from . import dates_utils


class TimeSeriesInterface(ABC):

    @abstractmethod
    def returns(self, start_date: datetime, end_date: datetime, **kwargs):
        raise NotImplementedError()


def prep_returns(ts: Union[TimeSeriesInterface, pd.DataFrame, pd.Series], lookback: str, date: datetime = None, **kwargs) -> pd.Series:
    end_date = dates_utils.last_bday(date)
    start_date = dates_utils.date_window(date=end_date, lookback=lookback)

    if isinstance(ts, pd.Series) or isinstance(ts, pd.DataFrame):
        return ts.loc[start_date:date].fillna(0)

    return ts.returns(start_date=start_date, end_date=end_date, **kwargs)
