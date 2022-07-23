from typing import Union
import pandas as pd
import quantstats as qs

from pyportlib.portfolio import IPortfolio
from pyportlib.services.data_reader import DataReader
from pyportlib.utils import files_utils

OUT_DIR = files_utils.get_outputs_dir()


def full(ptf: Union[IPortfolio, pd.Series, pd.DataFrame],
         benchmark: Union[pd.Series, pd.DataFrame, str, Portfolio],
         name: str,
         rf=None) -> None:
    """
    Produces quantstats html report and saves it to the pyportlib outputs directory.

    :param ptf: portfolio object or strategy returns from Pandas
    :param benchmark: portfolio object or strategy returns from Pandas or a ticker
    :param name: name of saved file
    :param rf: riskfree rate
    :return: None
    """
    if isinstance(ptf, Portfolio):
        ptf.update_data(fundamentals_and_dividends=False)
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
