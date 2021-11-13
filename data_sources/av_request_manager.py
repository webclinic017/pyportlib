from datetime import datetime
from time import sleep

MAX_RPM = 5
count = 0
request_log = {}


def request_limit():
    global count
    count += 1
    request_log[count] = datetime.now()
    if count > MAX_RPM:
        last = request_log[1]
        delta = (datetime.now() - last).seconds
        if delta < 60:
            sleep(60-delta)
        count = 0
