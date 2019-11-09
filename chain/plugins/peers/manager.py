import time
import logging
import os
import random

from redis import Redis

from websocket import WebSocketTimeoutException

from chain.common.config import config
from chain.common.exceptions import PeerNotFoundException
from chain.common.plugins import load_plugin
from chain.common.utils import get_chain_version
from chain.plugins.peers.peer import (
    Peer,
    PeerConnectionRefused,
    PeerErrorResponse,
    PeerRateLimitExceeded,
)
from chain.plugins.peers.tasks import add_peer
from chain.plugins.peers.utils import ip_is_whitelisted

logger = logging.getLogger(__name__)


class PeerManager(object):

    key_active = "peer:active:{}"
    key_suspended = "peer:suspended:{}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.database = load_plugin("chain.plugins.database")

        # TODO: check DNS and NTP connectivitiy?

        self.redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

    def setup(self):
        # Clear the peers list in redis

        # TODO: We might not want to delete peers from redis, but we shoud put them
        # trough add_peer task so it correctly validates them
        keys = self.redis.keys(self.key_active.format("*"))
        keys.extend(self.redis.keys(self.key_suspended.format("*")))
        if keys:
            num = self.redis.delete(*keys)
            logger.info("Deleted %s peers from redis", num)
        self._populate_seed_peers()

    def peers(self):
        keys = self.redis.keys(self.key_active.format("*"))
        peers = self.redis.mget(keys)
        logger.info("Got %s peers from redis", len(peers))
        return [Peer.from_json(peer) for peer in peers if peer]

    def get_peer_by_ip(self, ip):
        peer = self.redis.get(self.key_active.format(ip))
        if peer:
            return Peer.from_json(peer)
        return None

    def peer_with_ip_exists(self, ip):
        return self.redis.exists(self.key_active.format(ip))

    def is_peer_suspended(self, peer):
        return self.redis.exists(self.key_suspended.format(peer.ip))

    def get_peer(self, ip):
        peer = self.redis.get(self.key_active.format(ip))
        if peer:
            Peer.from_json(peer)
        return None

    def _populate_seed_peers(self):
        peer_list = config.peers["list"]
        for peer_obj in peer_list:
            add_peer(
                ip=peer_obj["ip"],
                port=peer_obj["port"],
                chain_version=get_chain_version(),
                nethash=config.network["nethash"],
                os=None,
            )

    def get_random_peer(self):
        peers = [peer for peer in self.peers()]
        if peers:
            return random.choice(peers)
        else:
            raise PeerNotFoundException("Can't find an active peer.")

    def fetch_blocks(self, from_height):
        # TODO: Missing error handling
        tries = 3
        while True:
            peer = self.get_random_peer()
            logger.info(
                "Downloading blocks from height %s via %s", from_height, peer.ip
            )
            try:
                return peer.fetch_blocks_from_height(from_height)
            except (
                PeerRateLimitExceeded,
                WebSocketTimeoutException,
                PeerErrorResponse,
                PeerConnectionRefused,
            ) as e:
                # TODO: suspend peer
                # self.suspend_peer(peer)
                logger.info(str(e))
                tries -= 1
                time.sleep(1)
                if tries == 0:
                    raise e

    def suspend_peer(self, peer):
        if ip_is_whitelisted(peer.ip):
            logger.info(
                "Peer %s:%s can't be suspended as it's whitelisted", peer.ip, peer.port
            )
            return None

        logger.warning("Suspending peer %s:%s", peer.ip, peer.port)
        self.redis.delete(self.key_active.format(peer.ip))
        # TODO: also record for how long peer needs to be suspended
        self.redis.set(self.key_suspended.format(peer.ip), peer.to_json())

    def has_minimum_peers(self):
        return len(self.peers()) >= config.peers["minimum_network_reach"]
