from datetime import datetime
import pandas as pd
from portofolio import Position
import quantstats as qs
from portofolio.utils import dates_utils


def skew(pos: Position, lookback: str, date: datetime = None) -> float:
    returns = _prep_returns(pos=pos, lookback=lookback, date=date)
    return qs.stats.skew(returns=returns, prepare_returns=False)


def _prep_returns(pos: Position, lookback: str, date: datetime = None) -> pd.Series:
    if date:
        start_date = dates_utils.date_window(date=date, lookback=lookback)

    else:
        start_date = dates_utils.date_window(lookback=lookback)
        date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    return pos.prices.loc[start_date:date].pct_change()


if __name__ == "__main__":
    posit = Position("AAPL", "USD")
    print(skew(posit, "1y"))
