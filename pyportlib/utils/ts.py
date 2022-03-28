from datetime import datetime
import pandas as pd
from . import dates_utils
from ..utils.logger import logger


def prep_returns(pos, lookback: str, date: datetime = None, **kwargs) -> pd.Series:
    if date:
        start_date = dates_utils.date_window(date=date, lookback=lookback)
    else:
        start_date = dates_utils.date_window(lookback=lookback)
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        ts_type = pos.name
    except:
        ts_type = "pandas"

    if ts_type == "position":
        prices = pos.prices
        prices.name = pos.ticker
        return prices.loc[start_date:date].pct_change().fillna(0)

    if ts_type == "portfolio":
        ic = kwargs.get("include_cash") if kwargs.get("include_cash") else False
        if kwargs.get("include_cash"):
            del kwargs['include_cash']
        return pos.pct_daily_total_pnl(start_date=start_date, end_date=date, include_cash=ic, **kwargs).fillna(0)

    if ts_type == "pandas":
        return pos.loc[start_date:date].fillna(0)
    else:
        logger.logging.error(f"passed type ({pos.__class__}) unsupport")