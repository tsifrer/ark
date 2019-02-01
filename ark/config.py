import json


def get_config():
    config = {}
    with open('ark/genesis_block.json') as f:
        config['genesis_block'] = json.loads(f.read())

    with open('ark/network.json') as f:
        config['network'] = json.loads(f.read())

    return config
