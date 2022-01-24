import os
from pathlib import Path
from utils import logger


def check_file(directory: str, file: str) -> bool:
    """
    checks if demanded file exists in specified directory
    :param directory: string of the directory path
    :param file: filename in specified directory
    :return: True if file exists
    """
    if len(directory):
        my_file = Path(f"{directory}/{file}")
    else:
        my_file = Path(f"{file}")

    try:
        if my_file.is_file():
            return True
        else:
            return False
    except Exception as e:
        logger.logging.error(e)


def check_dir(directory) -> bool:
    """
    checks if directory exists
    :param directory: string of the directory path
    :return: True if directory exists
    """
    if os.path.exists(directory):
        return True
    else:
        return False


def make_dir(path) -> None:
    """
    Creates directory at specified path
    :param path: string of directory path
    :return: None
    """
    os.makedirs(path)
