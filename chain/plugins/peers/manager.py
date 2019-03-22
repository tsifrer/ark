import os
import random

from redis import Redis

from .peer import Peer
from .utils import is_valid_peer

from chain.common.plugins import load_plugin
from chain.common.utils import get_chain_version
from chain.config import Config
from chain.plugins.peers.tasks import add_peer


class PeerManager(object):

    key = 'peers'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = load_plugin('chain.plugins.database')

        # TODO: check DNS and NTP connectivitiy?

        self.redis = Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=os.environ.get('REDIS_PORT', 6379),
            db=os.environ.get('REDIS_DB', 0),
        )

    def setup(self):
        # Clear the peers list in redis
        self.redis.delete(self.key)
        self._populate_seed_peers()

    @property
    def peers(self):
        peers = self.redis.lrange(self.key, 0, 1000)
        print('Got {} peers from redis'.format(len(peers)))
        return [Peer.from_json(p) for p in peers]

    def get_peer(self, ip):
        # TODO: This is slow as it loads all peers. Maybe figure out how to get just
        # the specific one by using something else than redis list
        for peer in self.peers:
            if peer.ip == ip:
                return peer
        return None

    def _populate_seed_peers(self):
        config = Config()
        peer_list = config['peers']['list']
        # TODO: put this trough add_peer task
        for peer_obj in peer_list:
            add_peer(
                ip=peer_obj['ip'],
                port=peer_obj['port'],
                chain_version=get_chain_version(),
                nethash=config['network']['nethash'],
                os=None,
            )

    def get_random_peer(self):
        # TODO: If random peer can't be found, raise an exception and then handle it
        # in functions that use this function
        # TODO: filter peers if they are banned and by their download size first
        peers = [peer for peer in self.peers if is_valid_peer(peer)]
        if peers:
            return random.choice(peers)

    def _get_random_peer_to_download_blocks(self):
        peer = self.get_random_peer()
        if not peer:
            raise Exception("Can't find any valid peers")
        recent_block_ids = self.database.get_recent_block_ids()
        if not peer.has_common_blocks(recent_block_ids):
            # TODO: implement guard
            peer.no_common_blocks = True
            return self._get_random_peer_to_download_blocks()
        return peer

    # getRandomDownloadBlocksPeer
    def download_blocks(self, from_height):
        # TODO: Missing error handling
        peer = self._get_random_peer_to_download_blocks()
        if peer:
            print(
                'Downloading blocks from height {} via {}'.format(from_height, peer.ip)
            )
            blocks = peer.download_blocks(from_height)
            return blocks
        return []
