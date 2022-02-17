from typing import Union

import pandas as pd
import quantstats as qs

import portofolio
from portofolio.data_sources.data_reader import DataReader
from portofolio.utils import files_utils

OUT_DIR = "client_data/outputs/"
if not files_utils.check_dir(OUT_DIR):
    files_utils.make_dir(OUT_DIR)


def full_html(portfolio: Union[portofolio.Portfolio, pd.Series, pd.DataFrame],
              benchmark: Union[pd.Series, pd.DataFrame, str, portofolio.Portfolio],
              name: str,
              rf=None) -> None:
    """
    produces quantstats html report
    :param rf: riskfree rate
    :param portfolio: portfolio object or strategy returns
    :param benchmark: benchmark returns in % or ticker of benchmark
    :param name: name of saved file
    :return: None
    """
    if isinstance(portfolio, portofolio.Portfolio):
        portfolio.update_data()
        strategy_returns = portfolio.pct_daily_total_pnl(start_date=portfolio.start_date)
    else:
        strategy_returns = portfolio

    if rf is None:
        rf = 0.

    if isinstance(benchmark, str):
        dr = DataReader()
        dr.update_prices(ticker=benchmark)
        benchmark_returns = dr.read_prices(ticker=benchmark).pct_change()
        benchmark_returns = benchmark_returns.loc[benchmark_returns.index.isin(strategy_returns.index)]
    elif isinstance(benchmark, portofolio.Portfolio):
        benchmark.update_data()
        benchmark_returns = benchmark.pct_daily_total_pnl(start_date=benchmark.start_date)
    elif isinstance(benchmark, pd.Series) or isinstance(benchmark, pd.DataFrame):
        benchmark_returns = benchmark
    else:
        raise ValueError("Benchmark error")

    title = f"{OUT_DIR}{name}.html"
    qs.reports.html(strategy_returns,
                    benchmark=benchmark_returns,
                    output=title,
                    title=title,
                    download_filename=title,
                    rf=rf)
