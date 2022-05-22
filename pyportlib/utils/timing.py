import atexit
from time import time, strftime, localtime
from datetime import timedelta


def _seconds_to_str(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return str(timedelta(seconds=elapsed))


def _log(s, elapsed=None):
    line = "="*40
    print(line)
    print(_seconds_to_str(), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()


def log(msg: str) -> None:
    """
    Log (Print) the elapsed time with a msg
    :param msg: String
    :return:
    """
    end = time()
    elapsed = end-start
    _log(msg, _seconds_to_str(elapsed))


def _endlog():
    end = time()
    elapsed = end-start
    _log("End Program", _seconds_to_str(elapsed))


start = time()
atexit.register(_endlog)
_log("Start Program")