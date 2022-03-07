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


def rolling_skew(pos: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252):
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).skew()


def kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.kurtosis()


def rolling_kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252):
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).kurt()


def beta(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None):
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    matrix = np.cov(returns, benchmark)
    return matrix[0, 1] / matrix[1, 1]


def rolling_beta(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252):
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    df = pd.DataFrame(data={"returns": returns, "benchmark": benchmark})

    corr = df.rolling(int(rolling_period)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(rolling_period)).std()
    rolling_b = corr * std['returns'] / std['benchmark']
    return rolling_b


def annualized_vol(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return qs.stats.volatility(returns=returns, prepare_returns=False, annualize=True)


def co_kurtosis(df, bias=False, fisher=True, variant='middle'):
    if variant not in {'left', 'right', 'middle'}:
        raise ValueError(f"variant {variant} not supported. choose ('left', 'right', 'middle')")
    v = df.values
    s1 = sigma = v.std(0, keepdims=True)
    means = v.mean(0, keepdims=True)

    # means is 1 x n (n is number of columns
    # this difference broacasts appropriately
    v1 = v - means

    s2 = sigma ** 2
    s3 = sigma ** 3

    v2 = v1 ** 2
    v3 = v1 ** 3

    m = v.shape[0]

    if variant in ['left', 'right']:
        kurt = pd.DataFrame(v3.T.dot(v1) / s3.T.dot(s1) / m, df.columns, df.columns)
        if variant == 'right':
            kurt = kurt.T
    else:
        kurt = pd.DataFrame(v2.T.dot(v2) / s2.T.dot(s2) / m, df.columns, df.columns)

    if not bias:
        kurt = kurt * (m ** 2 - 1) / (m - 2) / (m - 3) - 3 * (m - 1) ** 2 / (m - 2) / (m - 3)
    if not fisher:
        kurt += 3

    return kurt

#######


def prep_returns(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> pd.Series:
    if date:
        start_date = dates_utils.date_window(date=date, lookback=lookback)
    else:
        start_date = dates_utils.date_window(lookback=lookback)
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if isinstance(pos, Position):
        return pos.prices.loc[start_date:date].pct_change().dropna()
    if isinstance(pos, pd.Series):
        return pos.loc[start_date:date].dropna()


if __name__ == "__main__":
    posit = Position("AAPL", "USD")
    bench = Position("SPY", "USD")
    print(beta(posit, bench, lookback="1y"))
    rolling_beta(posit, bench, lookback="6m", rolling_period=10).plot()
    rolling_skew(posit, lookback="6m", rolling_period=10).plot()
    rolling_kurtosis(posit, lookback="6m", rolling_period=10).plot()

