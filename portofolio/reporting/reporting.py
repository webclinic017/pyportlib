from typing import Union

import pandas as pd
import quantstats as qs

from portofolio.data_sources.data_reader import DataReader
from portofolio.utils import files_utils

OUT_DIR = "client_data/outputs/"
if not files_utils.check_dir(OUT_DIR):
    files_utils.make_dir(OUT_DIR)


def full_html(strategy_returns: pd.Series, benchmark: Union[pd.Series, str], name: str, rf=None) -> None:
    """
    produces quantstats html report
    :param rf: riskfree rate
    :param strategy_returns: strategy returns in %
    :param benchmark: benchmark returns in % or ticker of benchmark
    :param name: name of saved file
    :return: None
    """
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
