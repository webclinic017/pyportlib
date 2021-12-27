from typing import Union

import pandas as pd
import quantstats as qs

from data_sources.data_reader import DataReader


def report(strategy_returns: pd.Series, benchmark: Union[pd.Series, str], name: str):
    """
    produces quantstats html report
    :param strategy_returns: strategy returns
    :param benchmark: benchmark returns or ticker of benchmark
    :param name: name of saved file
    :return: None
    """

    if isinstance(benchmark, str):
        benchmark = DataReader().read_prices(ticker=benchmark).pct_change()

    qs.reports.html(strategy_returns,
                    benchmark=benchmark,
                    output=f"client_data/outputs/{name}.html")
