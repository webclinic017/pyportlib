from datetime import datetime

import pyportlib as p

ptf = p.Portfolio("questrade_tfsa", "CAD")
# ptf.pct_daily_total_pnl(start_date=datetime(2022, 7, 1),
#                         end_date=datetime(2022, 7, 5),
#                         include_cash=True,
#                         )

ptf.positions.get("XIU.TO").daily_total_pnl(start_date=datetime(2022, 7, 1),
                                            end_date=datetime(2022, 7, 5),
                                            fx=ptf._fx)
