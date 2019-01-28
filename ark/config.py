import inspect
import json
from importlib import import_module




def get_config():
    config = {}
    with open('ark/genesis_block.json') as f:
        config['genesis_block'] = json.loads(f.read())
    return config





