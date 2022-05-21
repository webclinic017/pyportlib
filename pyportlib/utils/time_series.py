from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union, Tuple

import numpy as np
import pandas as pd

from . import dates_utils


class TimeSeriesInterface(ABC):
    """
    Interface from object that have returns for stats and plots
    """
    @abstractmethod
    def returns(self, start_date: datetime, end_date: datetime, **kwargs):
        raise NotImplementedError()


def prep_returns(ts: Union[TimeSeriesInterface, pd.DataFrame, pd.Series], lookback: str = None, date: datetime = None, **kwargs) -> pd.Series:
    """
    Computes returns for a Position, Portfolio or Pandas objects
    :param ts: TimeSeriesInterface Object (Position, Portfolio) or Pandas object
    :param lookback: string determining the start date. ex: '1y'
    :param date: end date of observation
    :param kwargs: PnL keyword arguments for Portfolio (tags, positions_to_exclude, include_cash)
    :return:
    """
    if lookback is None:
        lookback = "1y"
    end_date = dates_utils.last_bday(date)
    start_date = dates_utils.date_window(date=end_date, lookback=lookback)

    if isinstance(ts, pd.Series) or isinstance(ts, pd.DataFrame):
        series = ts.loc[start_date:date].fillna(0)
    else:
        series = ts.returns(start_date=start_date, end_date=end_date, **kwargs)
    series = remove_consecutive_zeroes(series)
    return series


def match_index(series1: pd.Series, series2: pd.Series) -> Tuple[pd.Series, pd.Series]:
    if len(series1) < len(series2):
        return series1, series2.loc[series2.index.isin(series1.index)]
    elif len(series1) > len(series2):
        return series1.loc[series1.index.isin(series2.index)], series2
    else:
        return series1, series2


def remove_consecutive_zeroes(series: pd.Series, threshold: int = 4) -> pd.Series:
    to_drop = series.eq(0).rolling(threshold).sum().isin([threshold, np.NaN])
    return series.loc[~to_drop]
