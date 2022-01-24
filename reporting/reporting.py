from typing import Union

import pandas as pd
import quantstats as qs

from data_sources.data_reader import DataReader


def full_html(strategy_returns: pd.Series, benchmark: Union[pd.Series, str], name: str, rf=None):
    """
    produces quantstats html report
    :param rf: riskfree rate
    :param strategy_returns: strategy returns
    :param benchmark: benchmark returns or ticker of benchmark
    :param name: name of saved file
    :return: None
    """
    if rf is None:
        rf = 1.5
    if isinstance(benchmark, str):
        dr = DataReader()
        dr.update_prices(ticker=benchmark)
        benchmark = dr.read_prices(ticker=benchmark).pct_change()
        benchmark = benchmark.loc[benchmark.index.isin(strategy_returns.index)]

    title = f"client_data/outputs/{name}.html"
    qs.reports.html(strategy_returns,
                    benchmark=benchmark,
                    output=title,
                    title=title,
                    download_filename=title,
                    rf=rf)
