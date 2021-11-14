from datetime import datetime
from typing import List
import pandas_market_calendars as mcal


def get_market_days(start: datetime, end: datetime = None, market: str = None) -> List[datetime]:
    if market is None:
        market = 'NYSE'
    if end is None:
        end = datetime.today()
    # TSX is TRT
    index = mcal.date_range(mcal.get_calendar(market).schedule(start_date=start, end_date=end), frequency='1D')

    return [d.strftime("%Y-%m-%d") for d in index]
