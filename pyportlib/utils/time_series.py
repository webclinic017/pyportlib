from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union
import pandas as pd

from . import dates_utils


class TimeSeriesInterface(ABC):
    """
    Interface from object that have returns for stats and plots
    """
    @abstractmethod
    def returns(self, start_date: datetime, end_date: datetime, **kwargs):
        raise NotImplementedError()


def prep_returns(ts: Union[TimeSeriesInterface, pd.DataFrame, pd.Series], lookback: str, date: datetime = None, **kwargs) -> pd.Series:
    """
    Computes returns for a Position, Portfolio or Pandas objects
    :param ts: time series object
    :param lookback:
    :param date:
    :param kwargs:
    :return:
    """
    end_date = dates_utils.last_bday(date)
    start_date = dates_utils.date_window(date=end_date, lookback=lookback)

    if isinstance(ts, pd.Series) or isinstance(ts, pd.DataFrame):
        return ts.loc[start_date:date].fillna(0)

    return ts.returns(start_date=start_date, end_date=end_date, **kwargs)
