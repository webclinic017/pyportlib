import json


def fetch_key(api: str):
    with open('config.json') as myfile:
        data = json.loads(myfile.read())
    return data['api']['api_keys'][api]


def fetch_data_sources(source_type: str):
    with open('config.json') as myfile:
        data = json.loads(myfile.read())
    source = data['datasource'][source_type]

    return source


def fetch_max_rpm(source_type: str):
    with open('config.json') as myfile:
        data = json.loads(myfile.read())
    max_rpm = data['api']['max_rpm'][source_type]

    return int(max_rpm)
