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

    # Wait for a bit more than 3s for response in case the node you're pinging is
    # the official node and is trying to add you as their peer and your p2p is not
    # responding. When they ping you, they wait for 3 seconds for response and if they
    # don't get any, they reject your response even though the request to them was
    # valid
    peer.ping(timeout=3.5)

    if peer.healthy:
        peer_manager.redis.rpush(peer_manager.key, peer.to_json())
        print('Accepted new peer {}:{}'.format(peer.ip, peer.port))
    else:
        print('Could not accept new peer {}:{}'.format(peer.ip, peer.port))
