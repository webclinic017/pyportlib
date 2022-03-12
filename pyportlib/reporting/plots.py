from datetime import datetime
from typing import Union

import quantstats as qs
from ..position import Position
from ..portfolio import Portfolio
from ..stats.stats import prep_returns


def snapshot(pos: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position or Portfolio object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    qs.plots.snapshot(rets, **kwargs)


def returns(pos: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', log: bool = False, **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param log: returns will be converted to log returns if True
    :param kwargs: optional arguments passed to quantstas plots module,
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    if not log:
        qs.plots.returns(rets, prepare_returns=False, **kwargs)
    elif log:
        qs.plots.log_returns(rets, prepare_returns=False, **kwargs)


def distribution(pos: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    qs.plots.histogram(rets, prepare_returns=False, **kwargs)


def rolling_beta(pos: Union[Position, Portfolio], benchmark: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param benchmark:
    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    bench_rets = prep_returns(benchmark, date=date, lookback=lookback)

    qs.plots.rolling_beta(rets, benchmark=bench_rets, prepare_returns=False, **kwargs)


def rolling_vol(pos: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    qs.plots.rolling_volatility(rets, **kwargs)


def rolling_sharpe(pos: Union[Position, Portfolio], date: datetime = None, lookback: str = '1y', **kwargs):
    """

    :param pos: Position object to plot returns
    :param date: end date of observation
    :param lookback: string determining the start date. ex: '1y'
    :param kwargs: optional arguments passed to quantstas plots module
                    benchark returns pandas Series can be passed or a Position object
    :return:
    """
    rets = prep_returns(pos, date=date, lookback=lookback)
    if kwargs.get('benchmark'):
        kwargs['benchmark'] = prep_returns(kwargs.get('benchmark'), date=date, lookback=lookback)

    qs.plots.rolling_sharpe(rets, **kwargs)