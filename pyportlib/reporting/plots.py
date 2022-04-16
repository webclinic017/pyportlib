from datetime import datetime
import pandas as pd
import quantstats as qs
from scipy.stats import norm
from ..utils import ts
from ..utils import logger


def snapshot(pos, date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position or Portfolio object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    if kwargs.get('benchmark') is not None:
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.snapshot(rets, **kwargs)


def returns(pos, date: datetime = None, lookback: str = '1y', log: bool = False, **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param log: returns will be converted to log returns if True
    :param kwargs: optional arguments passed to quantstas plots module,
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    if kwargs.get('benchmark') is not None:
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    if not log:
        if rets.empty:
            logger.logging.error(f"{pos.ticker} prices missing")
            return
        qs.plots.returns(rets, prepare_returns=False, **kwargs)
    elif log:
        qs.plots.log_returns(rets, prepare_returns=False, **kwargs)


def distribution(pos, date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    if kwargs.get('benchmark') is not None:
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.histogram(rets, prepare_returns=False, **kwargs)


def rolling_beta(pos, benchmark, date: datetime = None,
                 lookback: str = '1y', **kwargs):
    """

    :param benchmark:
    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    bench_rets = ts.prep_returns(benchmark, date=date, lookback=lookback)
    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.rolling_beta(rets, benchmark=bench_rets, prepare_returns=False, **kwargs)


def rolling_vol(pos, date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    if kwargs.get('benchmark') is not None:
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.rolling_volatility(rets, **kwargs)


def rolling_skew(pos, lookback: str, date: datetime = None,
                 rolling_period: int = 252, **kwargs):
    rets = ts.prep_returns(pos=pos, lookback=lookback, date=date, **kwargs)
    roll = rets.rolling(int(rolling_period)).skew()

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_kurtosis(pos, lookback: str, date: datetime = None,
                     rolling_period: int = 252, **kwargs):
    rets = ts.prep_returns(pos=pos, lookback=lookback, date=date, **kwargs)
    roll = rets.rolling(int(rolling_period)).kurt()

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.returns(returns=roll, compound=False, cumulative=False, prepare_returns=False, **kwargs)


def rolling_sharpe(pos, date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = ts.prep_returns(pos, date=date, lookback=lookback, **kwargs)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.rolling_sharpe(rets, **kwargs)


def rolling_var(pos, date: datetime = None, lookback: str = '1y', rolling_period: int = 252,
                quantile=0.95, **kwargs):
    rets = ts.prep_returns(pos=pos, lookback=lookback, date=date)
    mean = rets.rolling(rolling_period).mean()
    var = rets.rolling(rolling_period).std()
    stat = norm.ppf(1 - quantile, mean, var)
    roll_var = pd.Series(stat, index=rets.index).dropna() * -1

    if kwargs.get('benchmark') is not None:
        kwargs['benchmark'] = ts.prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if kwargs.get('positions_to_exclude'):
        del kwargs['positions_to_exclude']
    if kwargs.get("include_cash"):
        del kwargs['include_cash']
    qs.plots.returns(roll_var, compound=False, prepare_returns=False, **kwargs)
