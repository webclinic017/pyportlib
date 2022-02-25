import json
from datetime import datetime
from time import sleep
from utils import logger
from utils.config_utils import fetch_max_rpm

MAX_RPM = fetch_max_rpm('AlphaVantage')
count = 0
request_log = {}


def request_limit_manager(name: str = '', restarted: bool = False):
    global count
    count += 1
    now = datetime.now()

    if restarted:
        count = MAX_RPM
        with open('data_sources/logs/av_last_request.json') as f:
            last_request = datetime.strptime(json.loads(f.read())['last_request'], "%Y-%m-%d, %H:%M:%S")

    else:
        request_log[count] = now

        with open('data_sources/logs/av_last_request.json', 'w', encoding='utf-8') as f:
            json.dump({'last_request': now.strftime("%Y-%m-%d, %H:%M:%S")}, f, ensure_ascii=False, indent=1)

        logger.logging.info(f'AV request made for {name} at {datetime.now()}')
    
    if count >= MAX_RPM:
        last = request_log.get(1) if not restarted else last_request
        delta = (now - last).seconds
        if delta < 60:

            logger.logging.info(f'waiting for api... {60 - delta} seconds before next request')
            sleep(60-delta)
        count = 0
