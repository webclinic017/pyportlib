from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd
from ..position import Position
import quantstats as qs
from pyportlib.utils import dates_utils


def skew(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.skew()


def rolling_skew(pos: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).skew()


def kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.kurtosis()


def rolling_kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).kurt()


def beta(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    matrix = np.cov(returns, benchmark)
    return matrix[0, 1] / matrix[1, 1]


def rolling_beta(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    df = pd.DataFrame(data={"returns": returns, "benchmark": benchmark})

    corr = df.rolling(int(rolling_period)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(rolling_period)).std()
    rolling_b = corr * std['returns'] / std['benchmark']
    return rolling_b


def annualized_volatility(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return qs.stats.volatility(returns=returns, prepare_returns=False, annualize=True)


def rolling_volatility(pos: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(rolling_period).std() * np.sqrt(252)


def prep_returns(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> pd.Series:
    if date:
        start_date = dates_utils.date_window(date=date, lookback=lookback)
    else:
        start_date = dates_utils.date_window(lookback=lookback)
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if isinstance(pos, Position):
        prices = pos.prices
        prices.name = pos.ticker
        return prices.loc[start_date:date].pct_change().dropna()
    if isinstance(pos, pd.Series):
        return pos.loc[start_date:date].dropna()


if __name__ == "__main__":
    pass

