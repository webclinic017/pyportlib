from typing import Union

import pandas as pd
import quantstats as qs

import portofolio
from portofolio.data_sources.data_reader import DataReader
from portofolio.utils import files_utils

OUT_DIR = "client_data/outputs/"
if not files_utils.check_dir(OUT_DIR):
    files_utils.make_dir(OUT_DIR)


# TODO add start and end date with defaults
def full_html(portfolio: portofolio.Portfolio, benchmark: Union[pd.Series, str], name: str, rf=None) -> None:
    """
    produces quantstats html report
    :param rf: riskfree rate
    :param portfolio: portfolio object
    :param benchmark: benchmark returns in % or ticker of benchmark
    :param name: name of saved file
    :return: None
    """

    portfolio.update_data()
    strategy_returns = portfolio.pct_daily_total_pnl(start_date=portfolio.start_date)

    if rf is None:
        rf = 0.
    if isinstance(benchmark, str):
        dr = DataReader()
        dr.update_prices(ticker=benchmark)
        benchmark = dr.read_prices(ticker=benchmark).pct_change()
        benchmark = benchmark.loc[benchmark.index.isin(strategy_returns.index)]

    title = f"{OUT_DIR}{name}.html"
    qs.reports.html(strategy_returns,
                    benchmark=benchmark,
                    output=title,
                    title=title,
                    download_filename=title,
                    rf=rf)
