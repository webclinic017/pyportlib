from datetime import datetime
import scipy.cluster.hierarchy as sch
import numpy as np
import pandas as pd
from scipy.stats import norm
import quantstats as qs

from pyportlib.utils.time_series import TimeSeriesInterface
from pyportlib.utils import time_series


def skew(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    """
    Compute the skew of the returns distribution from a TimeSeries object

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return returns.skew()


def kurtosis(pos: TimeSeriesInterface, lookback: str, date: datetime = None, **kwargs) -> float:
    """
    Compute the kurtosis of the returns distribution from a TimeSeries object

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return returns.kurtosis()


def beta(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    """
    Compute the beta of the returns distribution from a TimeSeries object on a benchmark on the specified time period.

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param benchmark: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series on which to compute Beta
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    matrix = np.cov(returns, benchmark)
    return round(matrix[0, 1] / matrix[1, 1], 2)


def alpha(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    """
    Compute the alpha of the returns distribution from a TimeSeries object on a benchmark on the specified time period.

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param benchmark: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series on which to compute Beta
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    matrix = np.cov(returns, benchmark)
    bet = matrix[0, 1] / matrix[1, 1]
    alph = returns.mean() - (bet * benchmark.mean())
    return alph*len(returns)


def rolling_alpha(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, lookback: str = None, date: datetime = None, rolling_period: int = 252, **kwargs) -> pd.Series:
    # FIXME not ok
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    benchmark = time_series.prep_returns(ts=benchmark, lookback=lookback, date=date)
    returns, benchmark = time_series.match_index(returns, benchmark)
    df = pd.DataFrame(data={"returns": returns, "benchmark": benchmark})

    corr = df.rolling(int(rolling_period)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(rolling_period)).std()
    rolling_b = corr * std['returns'] / std['benchmark']

    rolling_alph = returns.rolling(int(rolling_period)).mean() - (rolling_b * benchmark.rolling(int(rolling_period)).mean())
    return rolling_alph * rolling_period


def annualized_volatility(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, **kwargs) -> float:
    """
    Compute the annualized volatility of the returns distribution from a TimeSeries object

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """
    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    return qs.stats.volatility(returns=returns, prepare_returns=False, annualize=True)


def value_at_risk(pos, lookback: str, date: datetime = None, quantile=0.95, method: str = "gaussian", **kwargs) -> float:
    """
    Compute the value at risk of the returns distribution from a TimeSeries object with a specified quantile and method

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param quantile: Quantile on which to compite VaR
    :param method: VaR compute method. 'gaussian' and 'historical' are implemented
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """

    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    if method == "gaussian":
        var = qs.stats.value_at_risk(returns=returns, confidence=quantile, prepare_returns=False)
        return abs(var)

    if method == "historical":
        var = returns.quantile(q=1 - quantile)
        return abs(var)

    raise NotImplementedError(f"{method}")


def rolling_var(pos, lookback: str = None, date: datetime = None, rolling_period: int = 252, quantile=0.95, **kwargs) -> pd.DataFrame:
    """
    Compute the gaussian rolling value at risk of the returns distribution from a TimeSeries object
    with a specified quantile.

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param date: Date to lookback from
    :param rolling_period: Number of trading days for the rolling period
    :param quantile: Quantile on which to compite VaR
    :param kwargs: Portfolio PnL or Position PnL kwargs
    :return:
    """

    returns = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)
    mean = returns.rolling(rolling_period).mean()
    var = returns.rolling(rolling_period).std()
    stat = norm.ppf(1-quantile, mean, var)
    return pd.Series(stat, index=returns.index).dropna() * -1


def cluster_corr(corr_array, inplace=False):
    """
    Rearranges the correlation matrix, corr_array, so that groups of highly
    correlated variables are next to eachother. https://wil.yegelwel.com/cluster-correlation-matrix/

    :param corr_array: pandas.DataFrame or numpy.ndarray a NxN correlation matrix
    :param inplace: bool
    :return:
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
