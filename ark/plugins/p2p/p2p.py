from ark.settings import PLUGINS


class P2P(object):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

        # TODO: check DNS and NTP connectivitiy?

        self.peers = []


    @property
    def database(self):
        return PLUGINS['database']

    def populate_seed_peers(self):
        peer_list = self.app.config['peers']['list']



    # def get_random_peer(self):


    # def download_blocks(from_height):

    # recent_block_ids = self.database.get_recent_block_ids()
        random_peer = None