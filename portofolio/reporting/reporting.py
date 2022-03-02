from typing import Union
import pandas as pd
import quantstats as qs
from ..portfolio import Portfolio
from ..data_sources.data_reader import DataReader
from ..utils import files_utils

OUT_DIR = files_utils.get_outputs_dir()


def full_html(ptf: Union[Portfolio, pd.Series, pd.DataFrame],
              benchmark: Union[pd.Series, pd.DataFrame, str, Portfolio],
              name: str,
              rf=None) -> None:
    """
    produces quantstats html report
    :param rf: riskfree rate
    :param ptf: portfolio object or strategy returns
    :param benchmark: benchmark returns in % or ticker of benchmark, portfolio object or series
    :param name: name of saved file
    :return: None
    """
    if isinstance(ptf, Portfolio):
        ptf.update_data()
        strategy_returns = ptf.pct_daily_total_pnl(start_date=ptf.start_date)
    else:
        strategy_returns = ptf

    if rf is None:
        rf = 0.

    if isinstance(benchmark, str):
        dr = DataReader()
        dr.update_prices(ticker=benchmark)
        benchmark_returns = dr.read_prices(ticker=benchmark).pct_change()
        benchmark_returns = benchmark_returns.loc[benchmark_returns.index.isin(strategy_returns.index)]
    elif isinstance(benchmark, Portfolio):
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
