from chain.common.plugins import load_plugin
from chain.hughie.config import huey
from chain.config import Config

from .peer import Peer


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

    if not peer.is_valid() or peer_manager.is_peer_suspended(peer):
        print('Peer {}:{} is invalid or suspended.'.format(peer.ip, peer.port))
        return

    if peer_manager.get_peer_by_ip(peer.ip):
        print('Peer {}:{} already exists.'.format(peer.ip, peer.port))
        return

    # Wait for a bit more than 3s for response in case the node you're pinging is
    # the official node and is trying to add you as their peer and your p2p is not
    # responding. When they ping you, they wait for 3 seconds for response and if they
    # don't get any, they reject your response even though the request to them was
    # valid
    # try:
    
    peer.verify_peer()

    print('DONE VERIFYING')
    print(peer.verification)

    peer_manager.redis.set(peer_manager.key_active.format(peer.ip), peer.to_json())

    # except:  # TODO: verify_peer should return just specific exception, handle it here
    # peer_manager.suspend_peer(peer)
    # if peer.healthy:
        
    #     print('Accepted new peer {}:{}'.format(peer.ip, peer.port))
    # else:
    #     print('Could not accept new peer {}:{}'.format(peer.ip, peer.port))
    # TODO: Suspend peer if it's not verified
