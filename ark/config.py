import json

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

        self._load_milestones()

        # TODO: get this from config somewhere
        self['fast_rebuild'] = False

    def _load_milestones(self):
        with open('ark/milestones.json') as f:
            milestones = json.loads(f.read())
        milestones.sort(key=itemgetter('height'))
        self['milestones'] = milestones

    def get_milestone(self, height):
        milestone = self['milestones'][0]
        for ms in reversed(self['milestones']):
            if height <= milestone['height']:
                milestone = ms
                break

        return milestone
