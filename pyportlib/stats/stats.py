from datetime import datetime
from typing import Union
import scipy.cluster.hierarchy as sch
import numpy as np
import pandas as pd
from ..position import Position
from .. import portfolio
import quantstats as qs
from pyportlib.utils import dates_utils


def skew(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.skew()


def rolling_skew(pos: Union[Position, pd.Series], lookback: str, date: datetime = None,
                 rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).skew()


def kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.kurtosis()


def rolling_kurtosis(pos: Union[Position, pd.Series], lookback: str, date: datetime = None,
                     rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(int(rolling_period)).kurt()


def beta(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str,
         date: datetime = None) -> float:
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


def alpha(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    matrix = np.cov(returns, benchmark)
    bet = matrix[0, 1] / matrix[1, 1]
    alph = returns.mean() - (bet * benchmark.mean())
    return alph*len(returns)


def rolling_alpha(pos: Union[Position, pd.Series], benchmark: Union[Position, pd.Series], lookback: str, date: datetime = None, rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    benchmark = prep_returns(pos=benchmark, lookback=lookback, date=date)
    df = pd.DataFrame(data={"returns": returns, "benchmark": benchmark})

    corr = df.rolling(int(rolling_period)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(rolling_period)).std()
    rolling_b = corr * std['returns'] / std['benchmark']

    rolling_alph = returns.rolling(int(rolling_period)).mean() - (rolling_b * benchmark.rolling(int(rolling_period)).mean())
    return rolling_alph*rolling_period


def annualized_volatility(pos: Union[Position, pd.Series], lookback: str, date: datetime = None) -> float:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return qs.stats.volatility(returns=returns, prepare_returns=False, annualize=True)


def rolling_volatility(pos: Union[Position, pd.Series], lookback: str, date: datetime = None,
                       rolling_period: int = 252) -> pd.Series:
    returns = prep_returns(pos=pos, lookback=lookback, date=date)
    return returns.rolling(rolling_period).std() * np.sqrt(252)


def prep_returns(pos, lookback: str, date: datetime = None, **kwargs) -> pd.Series:
    if date:
        start_date = dates_utils.date_window(date=date, lookback=lookback)
    else:
        start_date = dates_utils.date_window(lookback=lookback)
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if isinstance(pos, Position):
        prices = pos.prices
        prices.name = pos.ticker
        return prices.loc[start_date:date].pct_change().fillna(0)
    if isinstance(pos, pd.Series):
        return pos.loc[start_date:date].fillna(0)
    if isinstance(pos, portfolio.Portfolio):
        return pos.pct_daily_total_pnl(start_date=start_date, end_date=date, include_cash=False, **kwargs).fillna(0)


def cluster_corr(corr_array, inplace=False):
    """
    https://wil.yegelwel.com/cluster-correlation-matrix/
    Rearranges the correlation matrix, corr_array, so that groups of highly
    correlated variables are next to eachother

    Parameters
    ----------
    corr_array : pandas.DataFrame or numpy.ndarray
        a NxN correlation matrix
    inplace : bool

    Returns
    -------
    pandas.DataFrame or numpy.ndarray
        a NxN correlation matrix with the columns and rows rearranged
    """
    pairwise_distances = sch.distance.pdist(corr_array)
    linkage = sch.linkage(pairwise_distances, method='complete')
    cluster_distance_threshold = pairwise_distances.max() / 2
    idx_to_cluster_array = sch.fcluster(linkage, cluster_distance_threshold,
                                        criterion='distance')
    idx = np.argsort(idx_to_cluster_array)

    if not inplace:
        corr_array = corr_array.copy()

    if isinstance(corr_array, pd.DataFrame):
        return corr_array.iloc[idx, :].T.iloc[idx, :]
    return corr_array[idx, :][:, idx]


if __name__ == "__main__":
    pass
