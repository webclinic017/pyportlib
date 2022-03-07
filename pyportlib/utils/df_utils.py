from typing import List


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
