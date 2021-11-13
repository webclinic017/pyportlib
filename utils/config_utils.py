import json


def fetch_key(api: str):
    with open('config.json') as myfile:
        data = json.loads(myfile.read())
    return data['api']['api_keys'][api]
