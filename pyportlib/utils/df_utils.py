from typing import List


def check_df_columns(df, columns: List[str]) -> bool:
    """
    Checks if Pandas Dataframe contains columns
    :param df: Pandas Dataframe to be checked
    :param columns: columns to check
    :return: True if Pandas Dataframe contains all the columns
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
