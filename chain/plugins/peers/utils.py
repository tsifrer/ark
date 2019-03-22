from ipaddress import ip_address


def is_valid_peer(peer):
    try:
        ip = ip_address(peer.ip)
    except ValueError:
        print('Peer is invalid, because the IP is not a valid ip {}'.format(peer.ip))
        return False

    if ip.is_private:
        print('Peer is invalid, because the IP is private IP')
        return False

    if peer.no_common_blocks:
        print('Peer is invalid, as it has no common blocks')
        # TODO: This should be implemented as part of the guard thingy
        return False

    if not peer.healthy:
        print("Peer is invail as it's not healthy. Needs to eat more apples.")
        return False

    return True
