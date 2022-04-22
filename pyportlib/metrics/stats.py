from datetime import datetime
import scipy.cluster.hierarchy as sch
import numpy as np
import pandas as pd
from scipy.stats import norm
import quantstats as qs

from pyportlib.utils.time_series import TimeSeriesInterface
from ..utils import time_series


def skew(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return returns.skew()


def kurtosis(pos: TimeSeriesInterface, lookback: str, date: datetime = None, **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return returns.kurtosis()


def beta(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    matrix = np.cov(returns, benchmark)
    return round(matrix[0, 1] / matrix[1, 1], 2)


def alpha(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    matrix = np.cov(returns, benchmark)
    bet = matrix[0, 1] / matrix[1, 1]
    alph = returns.mean() - (bet * benchmark.mean())
    return alph*len(returns)


def rolling_alpha(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, rolling_period: int = 252, **kwargs) -> pd.Series:
    # FIXME not correct way to compute, maybe base on alpha function and loop dates...
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    df = pd.DataFrame(data={"returns": returns, "benchmark": benchmark})

    corr = df.rolling(int(rolling_period)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(rolling_period)).std()
    rolling_b = corr * std['returns'] / std['benchmark']

    rolling_alph = returns.rolling(int(rolling_period)).mean() - (rolling_b * benchmark.rolling(int(rolling_period)).mean())
    return rolling_alph*rolling_period


def annualized_volatility(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return qs.stats.volatility(returns=returns, prepare_returns=False, annualize=True)


def value_at_risk(pos, lookback: str, date: datetime = None, quantile=0.95, method: str = "gaussian", **kwargs) -> float:
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    if method == "gaussian":
        var = qs.stats.value_at_risk(returns=returns, confidence=quantile, prepare_returns=False)
        return abs(var)

    if method == "historical":
        var = returns.quantile(q=1 - quantile)
        return abs(var)


def rolling_var(pos, lookback: str = None, date: datetime = None, rolling_period: int = 252, quantile=0.95, **kwargs):
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    mean = returns.rolling(rolling_period).mean()
    var = returns.rolling(rolling_period).std()
    stat = norm.ppf(1-quantile, mean, var)
    return pd.Series(stat, index=returns.index).dropna() * -1


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
