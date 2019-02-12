import json
from hashlib import sha256
from operator import itemgetter


# def get_config():
#     config = {}
#     with open('ark/genesis_block.json') as f:
#         config['genesis_block'] = json.loads(f.read())

#     with open('ark/network.json') as f:
#         config['network'] = json.loads(f.read())

#     return config


class Config(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('ark/genesis_block.json') as f:
            self['genesis_block'] = json.loads(f.read())

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
        milestone = self['milestones'][0]
        for ms in reversed(self['milestones']):
            if height <= milestone['height']:
                milestone = ms
                break

        return milestone
