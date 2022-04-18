import json
from typing import List, Dict

from ..utils import files_utils


def make_config_dir(directory):
    if not files_utils.check_dir(directory):
        files_utils.make_dir(directory)


def fetch_tickers_to_ignore() -> List[str]:
    with open(f'{files_utils.get_config_dir()}config.json') as myfile:
        data = json.loads(myfile.read())
    tickers = data.get('ticker_ignore', None)

    if not tickers:
        return []
    return list(tickers.values())


def fetch_data_sources(source_type: str):
    with open(f'{files_utils.get_config_dir()}config.json') as myfile:
        data = json.loads(myfile.read())
    source = data['datasource'][source_type]

    return source


def create_default_config(directory):
    name = 'config.json'
    if not files_utils.check_file(directory, name):
        default_config = {
            "datasource": {
                "statements": "Yahoo",
                "market_data": "Yahoo"
            },
            "ticker_ignore": {
            }
        }
        with open(f'{directory}/{name}', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=1)
