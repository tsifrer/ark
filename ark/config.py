import json
from hashlib import sha256
from operator import itemgetter


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(dict, metaclass=Singleton):
    """
    TODO: Make this an object with fields like:
    self.genesis_block = data
    self.peers = [peers]
    self.milestones = [milestones]
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('INITIALZING CONFIG')

        with open('ark/genesis_block.json') as f:
            genesis_block = json.loads(f.read())
            for transaction in genesis_block['transactions']:
                transaction['version'] = 1
            self['genesis_block'] = genesis_block

        with open('ark/network.json') as f:
            self['network'] = json.loads(f.read())

        with open('ark/exceptions.json') as f:
            self['exceptions'] = json.loads(f.read())

        with open('ark/peers.json') as f:
            self['peers'] = json.loads(f.read())
            self['peers']['global_timeout'] = 30  # TODO: get this from somewhere

        self._load_milestones()

    def _calculate_milestone_hash(self, milestones):
        milestones_json = json.dumps(milestones)
        sha_hash = sha256(milestones_json.encode('utf-8')).hexdigest()
        return sha_hash[:16]

    def _load_milestones(self):
        with open('ark/milestones.json') as f:
            milestones = json.loads(f.read())
        milestones.sort(key=itemgetter('height'))
        self['milestones'] = milestones
        self['milestone_hash'] = self._calculate_milestone_hash(milestones)

    def get_milestone(self, height):
        for milestone in reversed(self['milestones']):
            if height >= milestone['height']:
                return milestone
