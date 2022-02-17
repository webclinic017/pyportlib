from datetime import datetime
import portofolio as porto

ptf = porto.Portfolio(account='tfsa', currency="CAD")
# ptf.update_data()
strategy_returns = ptf.pct_daily_total_pnl(start_date=ptf.start_date,
                                           include_cash=False,
                                           positions_to_exclude=['PLTR', 'SCYX']).iloc[1:]

bench = porto.Portfolio(account='bench_tfsa', currency='CAD')
# bench.update_data()

print(strategy_returns.iloc[-1])
porto.reporting.full_html(strategy_returns, bench, name=f"cash_npv_{ptf.account}_{datetime.today().date()}", rf=0.)
