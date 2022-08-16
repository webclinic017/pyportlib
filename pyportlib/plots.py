from datetime import datetime
import quantstats as qs

from pyportlib.portfolio.iportfolio import IPortfolio
from pyportlib import stats
from pyportlib.utils import time_series
from pyportlib.utils import logger
from pyportlib.utils.time_series import ITimeSeries


def snapshot(pos: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None, **kwargs):
    """
    Quantstats snapshot plot of returns

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    # we don't want to pass these arguments
    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]
    qs.plots.snapshot(rets, **kwargs)


def returns(pos: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None, log: bool = False,
            benchmark: ITimeSeries = None, **kwargs):
    """
    Quantstats plot of returns

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param log: returns will be converted to log returns if True
    :param benchmark: Position, Portfolio or Pandas object to plot benchamrk returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    if not log:
        qs.plots.returns(rets, benchmark=benchmark, prepare_returns=False, **kwargs)
    elif log:
        qs.plots.log_returns(rets, benchmark=benchmark, prepare_returns=False, **kwargs)


def distribution(pos: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None, **kwargs):
    """
    Quantstats plot of returns distribution

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.histogram(rets, prepare_returns=False, **kwargs)


def rolling_beta(pos: ITimeSeries, benchmark: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None,
                 **kwargs):
    """
    Quantstats plot of rolling beta

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param kwargs: PnL and Quantstats keyword arguments
    :return
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    benchmark = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date)
    rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_beta(rets, benchmark=benchmark, prepare_returns=False, **kwargs)


def rolling_vol(pos: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None,
                benchmark: ITimeSeries = None, **kwargs):
    """
    Quantstats plot of rolling volatility

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_volatility(rets, benchmark=benchmark, **kwargs)


def rolling_skew(pos: ITimeSeries, lookback: str = None, start_date: datetime = None, end_date: datetime = None, rolling_period: int = 252,
                 **kwargs):
    """
    Plot of rolling skewness

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param rolling_period: Length of rolling period in days
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    roll = rets.rolling(int(rolling_period)).skew()

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_kurtosis(pos: ITimeSeries, lookback: str = None, start_date: datetime = None, end_date: datetime = None, rolling_period: int = 252,
                     **kwargs):
    """
    Plot of rolling kurtosis

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param rolling_period: Length of rolling period in days
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    roll = rets.rolling(int(rolling_period)).kurt()

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_sharpe(pos: ITimeSeries, start_date: datetime = None, end_date: datetime = None, lookback: str = None,
                   benchmark: ITimeSeries = None, **kwargs):
    """
    Quantstats plot of rolling sharp ratio

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param benchmark: Position, Portfolio or Pandas object to plot benchmark returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date)
        rets, benchmark = time_series.match_index(rets, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.rolling_sharpe(rets, benchmark=benchmark, **kwargs)


def rolling_var(pos: ITimeSeries,
                start_date: datetime = None, end_date: datetime = None,
                lookback: str = None,
                rolling_period: int = 252,
                quantile=0.95,
                benchmark: ITimeSeries = None, **kwargs):
    """
    Plots rolling value at risk on a specific quantile

    :param pos: TimeSeries Object (Portfolio, Position, Pandas DataFrame/Series
    :param lookback: String: ex. "1y", "15m". Only m and y is supported to generate look back. See date_window doc.
    :param start_date:
    :param end_date:
    :param rolling_period: Length of rolling period in days
    :param quantile: VaR percentile
    :param benchmark: Position, Portfolio or Pandas object to plot returns
    :param kwargs: PnL and Quantstats keyword arguments
    :return:
    """
    rets = time_series.prep_returns(ts=pos, lookback=lookback, start_date=start_date, end=end_date)
    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return

    roll_var = stats.rolling_var(pos=rets, lookback=lookback, start_date=start_date, end=end_date,
                                 rolling_period=rolling_period, quantile=quantile, **kwargs)

    if benchmark is not None:
        benchmark = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date)
        benchmark = stats.rolling_var(pos=benchmark, lookback=lookback, start_date=start_date, end=end_date,
                                      rolling_period=rolling_period, quantile=quantile, **kwargs)
        roll_var, benchmark = time_series.match_index(roll_var, benchmark)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    qs.plots.returns(roll_var, benchmark=benchmark, compound=False, prepare_returns=False, **kwargs)


def position_allocation(ptf: IPortfolio, date=None, **kwargs):
    try:
        weights = ptf.position_weights(date=date)
    except AttributeError:
        raise ValueError("Use a Portfolio object")

    weights.plot.pie(autopct='%1.1f%%', fontsize=12, **kwargs)


def strategy_allocation(ptf: IPortfolio, date=None, **kwargs):
    try:
        weights = ptf.strategy_weights(date=date)
    except AttributeError:
        raise ValueError("Use a Portfolio object")

    weights.plot.pie(autopct='%1.1f%%', fontsize=12, **kwargs)


def excess_returns(pos: ITimeSeries,
                   benchmark: ITimeSeries,
                   start_date: datetime = None, end_date: datetime = None,
                   lookback: str = None,
                   **kwargs):
    rets = time_series.prep_returns(pos, lookback=lookback, start_date=start_date, end=end_date, **kwargs)
    bench = time_series.prep_returns(benchmark, lookback=lookback, start_date=start_date, end=end_date, include_cash=False)

    if rets.empty:
        logger.logging.error(f"{pos} prices missing")
        return
    if bench.empty:
        logger.logging.error(f"benchmark prices missing")
        return

    rets, bench = time_series.match_index(rets, bench)

    kwargs_to_remove = ['positions_to_exclude', 'include_cash', 'tags']
    [kwargs.pop(key, None) for key in kwargs_to_remove]

    total = rets - bench
    qs.plots.returns(total, prepare_returns=False, **kwargs)
