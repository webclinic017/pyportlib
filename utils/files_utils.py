import os
from datetime import datetime
from pathlib import Path
import pandas as pd


def check_file(directory:str, file:str):
    my_file = Path(f"{directory}/{file}")
    try:
        if my_file.is_file():
            return True
        else:
            return False
    except:
        print('error suppressed in utils.check_file')
        return False


def check_dir(directory):

    if os.path.exists(directory):
        return True
    else:
        return False


def make_dir(path):
    os.makedirs(path)
