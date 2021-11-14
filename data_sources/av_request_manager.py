from datetime import datetime
from pprint import pprint
from time import sleep

MAX_RPM = 5
count = 0
request_log = {}


def request_limit(name: str = ''):
    global count
    count += 1
    request_log[count] = (datetime.now(), name)
    if count >= MAX_RPM:
        last = request_log.get(1)[0]
        delta = (datetime.now() - last).seconds
        if delta < 60:
            print('requests logged')
            pprint(request_log)
            print(f'waiting for api... {60-delta} seconds before next request')
            sleep(60-delta)
        count = 0
