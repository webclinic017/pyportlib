from typing import List


def check_csv(df, columns: List[str]):
    condition1 = set(df.columns) == set(columns)

    if condition1:
        return True
    else:
        return False
