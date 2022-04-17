from typing import List

import pandas as pd


def check_df_columns(df, columns: List[str]) -> bool:
    """
    Checks if dataframe contains columns
    :param df: dataframe to be checked
    :param columns: columns wanted
    :return: True if df contains the columns
    """
    condition1 = set(df.columns) == set(columns)

    if condition1:
        return True
    else:
        return False


def red_green_cmap(value):
    """
    Colors elements in a dateframe
    green if positive and red if
    negative. Does not color NaN
    values.
    """

    if value < 0:
        color = 'red'
    elif value > 0:
        color = 'green'
    else:
        color = 'black'

    return 'color: %s' % color
