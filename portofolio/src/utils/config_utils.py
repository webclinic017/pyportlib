import json

from utils import files_utils


def make_config_dir():
    if not files_utils.check_dir('config/'):
        files_utils.make_dir('config/')


def fetch_key(api: str):
    with open('config/config.json') as myfile:
        data = json.loads(myfile.read())
    return data['api']['api_keys'][api]


def fetch_data_sources(source_type: str):
    with open('config/config.json') as myfile:
        data = json.loads(myfile.read())
    source = data['datasource'][source_type]

    return source


def fetch_max_rpm(source_type: str):
    with open('config/config.json') as myfile:
        data = json.loads(myfile.read())
    max_rpm = data['api']['max_requests_per_minute'][source_type]

    return int(max_rpm)


def create_default_config():
    # create default config file
    file_name = 'config.json'
    dir = 'config'

    if not files_utils.check_file(dir, file_name):
        default_config = {
            "api": {
                "max_requests_per_minute": {
                    "AlphaVantage": 5
                },
                "api_keys": {
                    "SimFin": "ENTER_KEY",
                    "AlphaVantage": "ENTER_KEY"
                }
            },
            "datasource": {
                "statements": "YFinance",
                "market_data": "YFinance"
            }
        }
        with open(f'{dir}/{file_name}', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=1)

