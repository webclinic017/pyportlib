from datetime import datetime
import pandas as pd
import quantstats as qs
from scipy.stats import norm

from ..utils import time_series
from ..utils import logger
from ..utils.time_series import TimeSeriesInterface


def snapshot(pos: TimeSeriesInterface, date: datetime = None, lookback: str = None, **kwargs):
    """
    Quantstats plot of returns
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    # we don't want to pass these arguments
    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]
    qs.plots.snapshot(rets, **kwargs)


def returns(pos: TimeSeriesInterface, date: datetime = None, lookback: str = None, log: bool = False, benchmark: TimeSeriesInterface = None, **kwargs):
    """
    Quantstats plot of returns
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param log: returns will be converted to log returns if True
    :param benchmark: Position, Portfolio or Pandas object to plot benchamrk returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, date=date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    if not log:
        qs.plots.returns(rets, benchmark=benchmark, prepare_returns=False, **kwargs)
    elif log:
        qs.plots.log_returns(rets, benchmark=benchmark, prepare_returns=False, **kwargs)


def distribution(pos: TimeSeriesInterface, date: datetime = None, lookback: str = None, **kwargs):
    """
    Quantstats plot of returns distribution
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.histogram(rets, prepare_returns=False, **kwargs)


def rolling_beta(pos: TimeSeriesInterface, benchmark: TimeSeriesInterface, date: datetime = None, lookback: str = None, **kwargs):
    """
    Quantstats plot of rolling beta
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: PnL and Quantstats keyword arguments
    :return
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    benchmark = time_series.prep_returns(benchmark, lookback=lookback, date=date)
    rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_beta(rets, benchmark=benchmark, prepare_returns=False, **kwargs)


def rolling_vol(pos: TimeSeriesInterface, date: datetime = None, lookback: str = None, benchmark: TimeSeriesInterface = None, **kwargs):
    """
    Quantstats plot of rolling volatility
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, date=date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_volatility(rets, benchmark=benchmark, **kwargs)


def rolling_skew(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, rolling_period: int = 252, **kwargs):
    """
    Plot of rolling skewness
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param rolling_period: Length of rolling period in days
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    roll = rets.rolling(int(rolling_period)).skew()

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_kurtosis(pos: TimeSeriesInterface, lookback: str = None, date: datetime = None, rolling_period: int = 252, **kwargs):
    """
    Plot of rolling kurtosis
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param rolling_period: Length of rolling period in days
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    roll = rets.rolling(int(rolling_period)).kurt()

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_sharpe(pos: TimeSeriesInterface, date: datetime = None, lookback: str = None, benchmark: TimeSeriesInterface = None, **kwargs):
    """
    Quantstats plot of rolling sharp ratio
    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, date=date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, date=date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_sharpe(rets, benchmark=benchmark, **kwargs)


def rolling_var(pos: TimeSeriesInterface,
                date: datetime = None,
                lookback: str = None,
                rolling_period: int = 252,
                quantile=0.95,
                benchmark: TimeSeriesInterface = None, **kwargs):
    """

    :param pos: Position, Portfolio or Pandas object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param rolling_period: Length of rolling period in days
    :param quantile: VaR percentile
    :param benchmark: Position, Portfolio or Pandas object to plot returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, date=date)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    mean = rets.rolling(rolling_period).mean()
    var = rets.rolling(rolling_period).std()
    stat = norm.ppf(1 - quantile, mean, var)
    roll_var = pd.Series(stat, index=rets.index).dropna() * -1

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, date=date)
        rets, benchmark = time_series.match_index(roll_var, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(roll_var, benchmark=benchmark, compound=False, prepare_returns=False, **kwargs)
