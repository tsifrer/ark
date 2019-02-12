from ipaddress import ip_address


def is_valid_peer(peer):
    try:
        ip = ip_address(peer.ip)
    except ValueError:
        return False

    if ip.is_private:
        return False

    if not peer.healthy:
        return False

    return True
