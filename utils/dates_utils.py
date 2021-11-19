from datetime import datetime
from typing import List
import pandas_market_calendars as mcal
import pandas as pd


def get_market_days(start: datetime, end: datetime = None, market: str = None) -> List[datetime]:
    if market is None:
        market = 'NYSE'
    if end is None:
        end = datetime.today()
    # TSX is TRT
    index = mcal.date_range(mcal.get_calendar(market).schedule(start_date=start, end_date=end), frequency='1D')
    index = index.tz_convert(None)
    index = [i.replace(hour=0, minute=0, second=0, microsecond=0) for i in index]
    return index
