import os
from pathlib import Path

from pyportlib.utils.config_utils import create_default_config


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

    if my_file.is_file():
        return True
    else:
        return False


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


_client_dir = None
_data_dir = None
_accounts_dir = None
_price_data_dir = None
_fx_data_dir = None
_statements_data_dir = None
_config_dir = None
_outputs_dir = None


def _check_client_dir():
    """
    Raise an exception if the user has not set the data-directory.
    This is used instead of a really strange Python error-message.
    """
    if _data_dir is None:
        msg = 'The pyportlib data directory has not been set by the user. ' \
              'Please call the function pyportlib.set_data_dir() first.'
        raise Exception(msg)


def set_client_dir(data_dir=""):
    """
    Set the directory where datasets are stored on disk
    and create the directory if it does not exist.

    :param data_dir: String with the directory-name.
    :return: `None`
    """
    data_dir = f'~{data_dir}/portofolio_client_data'
    global _client_dir, _data_dir, _accounts_dir, _price_data_dir, \
        _fx_data_dir, _statements_data_dir, _config_dir, _outputs_dir

    # Expand directory if it begins with ~
    _client_dir = os.path.expanduser(data_dir)
    _data_dir = os.path.join(_client_dir, 'data/')
    _accounts_dir = os.path.join(_client_dir, 'accounts/')

    _price_data_dir = os.path.join(_data_dir, 'prices/')
    _fx_data_dir = os.path.join(_data_dir, 'fx/')
    _statements_data_dir = os.path.join(_data_dir, 'statements/')

    _config_dir = os.path.join(_client_dir, 'config/')
    _outputs_dir = os.path.join(_client_dir, 'outputs/')

    if not os.path.exists(_client_dir):
        os.makedirs(_client_dir)
    if not os.path.exists(_data_dir):
        os.makedirs(_data_dir)
    if not os.path.exists(_price_data_dir):
        os.makedirs(_price_data_dir)
    if not os.path.exists(_fx_data_dir):
        os.makedirs(_fx_data_dir)
    if not os.path.exists(_statements_data_dir):
        os.makedirs(_statements_data_dir)

    if not os.path.exists(_accounts_dir):
        os.makedirs(_accounts_dir)
    if not os.path.exists(_outputs_dir):
        os.makedirs(_outputs_dir)

    if not os.path.exists(_config_dir):
        os.makedirs(_config_dir)
    if not os.path.exists(f"{_config_dir}config.json"):
        create_default_config(_config_dir)


def get_client_dir():
    """
    Get the full path for the main data-directory where
    datasets are saved on disk.

    :return: String with the path for the data-directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _client_dir


def get_data_dir():
    """
    Get the full path for the data directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the download directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _data_dir


def get_accounts_dir():
    """
    Get the full path for the accounts directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the accounts directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _accounts_dir


def get_config_dir():
    """
    Get the full path for the accounts directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the accounts directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _config_dir


def get_price_data_dir():
    """
    Get the full path for the price directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the price directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _price_data_dir


def get_fx_data_dir():
    """
    Get the full path for the fx directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the fx directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _fx_data_dir


def get_statements_data_dir():
    """
    Get the full path for the statements directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the statements directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _statements_data_dir


def get_outputs_dir():
    """
    Get the full path for the statements directory where
    the files with datasets are temporarily stored.

    :return: String with the path for the statements directory.
    """
    # Ensure the data-directory has been set by the user.
    _check_client_dir()
    return _outputs_dir
