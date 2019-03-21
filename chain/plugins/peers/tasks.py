from chain.common.plugins import load_plugin
from chain.hughie.config import huey

from .peer import Peer
from .utils import is_valid_peer


@huey.task()
def add_peer(ip, port, chain_version, nethash, os):
    # TODO: Disable this function if peer discoverability is disabled in config

    peer_manager = load_plugin('chain.plugins.peers')

    peer = Peer(
        ip=ip,
        port=port,
        chain_version=chain_version,
        nethash=nethash,
        os=os,
    )

    if not is_valid_peer(peer) or peer_manager.get_peer(peer.ip):
        return

    peer.ping()

    if peer.healthy:
        peer_manager.redis.rpush(peer_manager.key, peer.to_json())
        print('Accepted new peer {}:{}'.format(peer.ip, peer.port))
    else:
        print('Could not accept new peer {}:{}'.format(peer.ip, peer.port))
