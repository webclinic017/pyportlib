from datetime import datetime
import portofolio as porto

ptf = porto.Portfolio(account='tfsa', currency="CAD")
ptf.update_data(fundamentals_and_dividends=False)

strategy_returns = ptf.pct_daily_total_pnl(start_date=ptf.start_date,
                                           include_cash=True).iloc[1:]

bench = porto.Portfolio(account='bench_tfsa', currency='CAD')

porto.reporting.full_html(strategy_returns,
                          bench,
                          name=f"cash_npv_{ptf.account}_{datetime.today().date()}",
                          rf=0.)
