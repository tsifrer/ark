import os
import random

from redis import Redis

from .peer import Peer

from chain.common.plugins import load_plugin
from chain.common.utils import get_chain_version
from chain.config import Config
from chain.plugins.peers.tasks import add_peer
from chain.common.exceptions import PeerNotFoundException


class PeerManager(object):

    key_active = 'peer:active:{}'
    key_suspended = 'peer:suspended:{}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = load_plugin('chain.plugins.database')

        # TODO: check DNS and NTP connectivitiy?

        self.redis = Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=os.environ.get('REDIS_PORT', 6379),
            db=os.environ.get('REDIS_DB', 0),
        )

        # TODO: peer discovery

    def setup(self):
        # Clear the peers list in redis

        # TODO: We might not want to delete peers from redis, but we shoud put them
        # trough add_peer task so it correctly validates them 
        keys = self.redis.keys(self.key_active.format('*'))
        keys.extend(self.redis.keys(self.key_suspended.format('*')))
        if keys:
            num = self.redis.delete(*keys)
            print('Deleted {} peers from redis'.format(num))
        self._populate_seed_peers()

    @property
    def peers(self):
        keys = self.redis.keys(self.key_active.format('*'))
        peers = self.redis.mget(keys)
        print('Got {} peers from redis'.format(len(peers)))
        return [Peer.from_json(peer) for peer in peers if peer]

    def get_peer_by_ip(self, ip):
        return self.redis.get(self.key_active.format(ip))

    def is_peer_suspended(self, peer):
        return self.redis.exists(self.key_suspended.format(peer.ip))

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
        peers = [peer for peer in self.peers]
        if peers:
            return random.choice(peers)

    def _get_random_peer_to_download_blocks(self):
        # TODO: Refactor as most of this is obsolete with the peer verification
        peer = self.get_random_peer()
        if not peer:
            raise PeerNotFoundException("Can't find any valid peers")
        # recent_block_ids = self.database.get_recent_block_ids()
        # if not peer.has_common_blocks(recent_block_ids):
        #     # TODO: implement guard
        #     peer.no_common_blocks = True
        #     return self._get_random_peer_to_download_blocks()
        return peer

    # getRandomDownloadBlocksPeer
    def fetch_blocks(self, from_height):
        # TODO: Missing error handling
        peer = self._get_random_peer_to_download_blocks()
        if peer:
            print(
                'Downloading blocks from height {} via {}'.format(from_height, peer.ip)
            )
            blocks = peer.fetch_blocks_from_height(from_height)
            return blocks
        return []
