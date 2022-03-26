from datetime import datetime, timedelta
from typing import List
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

from pyportlib.utils import logger


def get_market_days(start: datetime, end: datetime = None, market: str = None) -> List[datetime]:
    if market is None:
        market = 'NYSE'
    if end is None:
        end = datetime.today()
    if start is None:
        start = end
    # TSX is TRT
    try:
        index = mcal.date_range(mcal.get_calendar(market).schedule(start_date=start, end_date=end), frequency='1D')
        index = index.tz_convert(None)
        index = [i.replace(hour=0, minute=0, second=0, microsecond=0) for i in index]
    except ValueError:
        index = []
    except AttributeError:
        index = []
    return index


def date_window(lookback: str = "1y", date: datetime = None):
    amount = int(lookback[:-1])
    scale = lookback[-1]
    if date is None:
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if scale == "y":
        date = date + relativedelta(years=- amount)
    elif scale == "m":
        date = date + relativedelta(months=- amount)
    else:
        logger.logging.error(f"lookback scale {scale} not supported. choose (y or m)")

    return date

def last_bday():
    last = datetime.today()
    shift = timedelta(max(1, (last.weekday() + 6) % 7 - 3))
    return (last - shift).replace(hour=0, minute=0, second=0, microsecond=0)
