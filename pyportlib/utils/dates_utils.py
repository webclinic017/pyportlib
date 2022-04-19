from datetime import datetime, timedelta
from typing import List
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta
from pandas._libs.tslibs.offsets import BDay
import warnings

from ..utils import logger

warnings.filterwarnings('ignore')


def get_market_days(start: datetime, end: datetime = None, market: str = None) -> List[datetime]:
    """
    Generate datetime list (index) for a date range with a specific calendar
    :param start:
    :param end:
    :param market: market calendar
    :return:
    """
    if market is None:
        market = 'NYSE'
    if end is None:
        end = datetime.today()
    if start is None:
        start = end

    try:
        index = mcal.date_range(mcal.get_calendar(market).schedule(start_date=start, end_date=end), frequency='1D')
        index = index.tz_convert(None)
        index = [i.replace(hour=0, minute=0, second=0, microsecond=0) for i in index]
    except ValueError:
        index = []
    except AttributeError:
        index = []
    return index


def date_window(lookback: str = "1y", date: datetime = None) -> datetime:
    """
    Returns date with look back: ex. 2022-01-01 with lookback 1y is 2021-01-01.
    :param lookback: string: ex. "1y", "15m"
    :param date: date to lookback from
    :return:
    """
    amount = int(lookback[:-1])
    scale = lookback[-1]
    date = last_bday(as_of=date)

    if scale == "y":
        date = date + relativedelta(years=- amount)
    elif scale == "m":
        date = date + relativedelta(months=- amount)
    else:
        logger.logging.error(f"lookback scale {scale} not supported. choose (y or m)")

    return date


def last_bday(as_of: datetime = None) -> datetime:
    """
    Returns the last busniess day if as_of is not a business day.
    :param as_of: date
    :return:
    """
    if as_of is None:
        as_of = datetime.today()

        # before market open
        if as_of.hour < 9 and as_of.minute < 30:
            as_of = as_of - bday(1)

        as_of = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
    if as_of.isoweekday() in range(1, 6):
        last_bd = as_of
    else:
        shift = timedelta(max(1, (as_of.weekday() + 6) % 7 - 3))
        last_bd = (as_of - shift).replace(hour=0, minute=0, second=0, microsecond=0)

    # check if holiday
    check = get_market_days(start=last_bd, end=last_bd)
    if not check:
        return (last_bd - bday(1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return last_bd


def bday(n: int):
    """
    Pandas BDay wrapper
    :param n: number of days
    :return:
    """
    return BDay(n)
