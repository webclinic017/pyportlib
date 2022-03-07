from datetime import datetime
from typing import List
import pandas_market_calendars as mcal

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
    amount = int(lookback[0])
    scale = lookback[1]
    if date is None:
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    if scale == "y":
        date = date.replace(year=date.year - amount)
    elif scale == "m":
        date = date.replace(month=date.month - amount)
    else:
        logger.logging.error(f"lookback scale {scale} not supported. choose (y or m)")

    return date