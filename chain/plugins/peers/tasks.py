import random

from huey import crontab

from chain.common.plugins import load_plugin
from chain.hughie.config import huey
from chain.config import Config

from .peer import Peer


@huey.task()
def add_peer(ip, port, chain_version, nethash, os):
    # TODO: Disable this function if peer discoverability is disabled in config

    peer_manager = load_plugin("chain.plugins.peers")

    peer = Peer(ip=ip, port=port, chain_version=chain_version, nethash=nethash, os=os)

    if not peer.is_valid() or peer_manager.is_peer_suspended(peer):
        print("Peer {}:{} is invalid or suspended.".format(peer.ip, peer.port))
        return

    if peer_manager.peer_with_ip_exists(peer.ip):
        print("Peer {}:{} already exists.".format(peer.ip, peer.port))
        return

    # Wait for a bit more than 3s for response in case the node you're pinging is
    # the official node and is trying to add you as their peer and your p2p is not
    # responding. When they ping you, they wait for 3 seconds for response and if they
    # don't get any, they reject your response even though the request to them was
    # valid
    # try:
    try:
        peer.verify_peer()
    except:
        peer_manager.suspend_peer(peer)
    else:
        print(
            "Accepting peer {}:{}. Vefification: {}".format(
                peer.ip, peer.port, peer.verification
            )
        )
        peer_manager.redis.set(peer_manager.key_active.format(peer.ip), peer.to_json())


@huey.task()
def reverify_peer(ip):
    peer_manager = load_plugin("chain.plugins.peers")
    peer = peer_manager.get_peer_by_ip(ip)
    print("Reverifying peer {}:{}".format(peer.ip, peer.port))
    if peer:
        try:
            peer.verify_peer()
        except:
            peer_manager.suspend_peer(peer)
        else:
            print("Peer {}:{} successfully reverified".format(peer.ip, peer.port))
            peer_manager.redis.set(
                peer_manager.key_active.format(peer.ip), peer.to_json()
            )
    else:
        print("Couldn't find a peer to reverify")


@huey.task()
def reverify_all_peers():
    peer_manager = load_plugin("chain.plugins.peers")
    peers = peer_manager.peers()
    print("Reverifying all {} peers".format(len(peers)))
    for peer in peers:
        reverify_peer(peer.ip)


@huey.periodic_task(crontab(minute="*/10"))
def discover_peers():
    """
    Fetch peers of your existing peers to increase the number of peers.
    """
    # TODO: Disable this function if peer discoverability is disabled in config

    peer_manager = load_plugin("chain.plugins.peers")
    peers = peer_manager.peers()
    # Shuffle peers so we always get the peers from the different peers at the start
    random.shuffle(peers)
    for index, peer in enumerate(peers):
        his_peers = peer.fetch_peers()
        for his_peer in his_peers:
            add_peer(
                ip=his_peer.ip,
                port=his_peer.port,
                chain_version=his_peer.chain_version,
                nethash=his_peer.nethash,
                os=his_peer.os,
            )

        # Always get peers from at least 4 sources. As add_peer is async,
        # `has_minimum_peers` might actually return wrong result, but that will only
        # increase the number of peers we have.
        if index >= 4 and peer_manager.has_minimum_peers():
            break

    reverify_all_peers()
