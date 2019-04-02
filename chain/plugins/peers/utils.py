from chain.common.plugins import load_plugin
from chain.config import Config
from chain.crypto.utils import calculate_round


def ip_is_blacklisted(ip):
    config = Config()
    if ip in config['peers']['blacklist']:
        return True
    return False


def ip_is_whitelisted(ip):
    config = Config()
    if ip in config['peers']['whitelist']:
        return True
    return False


def _get_sample_heights(min_height, max_height, n_samples):
    step = (max_height - min_height) / (n_samples - 1)
    samples = []
    for x in range(n_samples):
        samples.append(min_height + round(step * x))

    # Dedupe samples while also retaining order
    unique = []
    for sample in samples:
        if sample not in unique:
            unique.append(sample)
    return unique


def _find_highest_common_between_heights(peer, heights):
    database = load_plugin('chain.plugins.database')
    print(
        'Checking for the highest common block height. Currently checking for heights {}'.format(
            heights
        )
    )
    our_blocks = database.get_blocks_by_heights(heights)
    if len(our_blocks) != len(heights):
        raise Exception(
            'Did not fetch all blocks with heights {} from the db'.format(heights)
        )

    # TODO: something something deadline

    heights_by_id = {}
    for block in our_blocks:
        heights_by_id[block.id] = block.height

    common = peer.fetch_common_block_by_ids(list(heights_by_id.keys()))
    if not common:
        print(
            "Couldn't find a common block for peer {}:{} for block heights {}".format(
                peer.ip, peer.port, heights
            )
        )
        return None

    if heights_by_id.get(common['id']) != common['height']:
        print(
            'Our block height {} does not match with peer height {} for block with id {}'.format(
                heights_by_id.get(common['id']), common['height'], common['id']
            )
        )
        return None
    return common['height']


def _find_highest_common_block_height(peer, min_height, max_height):
    n_samples = 9
    highest_matching = None

    while True:
        heights = _get_sample_heights(min_height, max_height, n_samples)
        common = _find_highest_common_between_heights(peer, heights)
        if not common:
            break
        highest_matching = common

        if highest_matching == heights[-1]:
            # We've found our match
            break

        if min_height + n_samples >= max_height:
            raise Exception('Checked for every height but could not find a match')

        min_height = highest_matching + 1
        max_height = heights[heights.index(highest_matching) + 1] - 1

    return highest_matching


def _is_valid_block(block, height, current_round, delegate_keys):
    verified, errors = block.verify()

    if not verified:
        print(
            "Peer's block at height {} does not pass crypto validation".format(height)
        )
        return False

    if block.height != height:
        print(
            "Peer's block height {} is different than the expected height {}".format(
                block.height.height
            )
        )
        return False

    if block.generator_public_key in delegate_keys:
        return True

    print(
        "Peer's block with id {} and height {} is not signed by any of the delegates for the corresponding round {}".format(
            block.id, block.height, current_round
        )
    )
    return False


def _verify_peer_blocks(peer, start_height, peer_height):
    database = load_plugin('chain.plugins.database')

    current_round, _, max_delegates = calculate_round(start_height)
    last_height_in_round = current_round * max_delegates
    first_height_in_round = (current_round - 1) * max_delegates + 1
    delegates = database.get_active_delegates(first_height_in_round)
    delegate_keys = [d.public_key for d in delegates]

    end_height = min(peer_height, last_height_in_round)

    height_block_map = {}
    for height in range(start_height, end_height + 1):
        if height not in height_block_map:
            # Height does not exist in our map yet, so get it from the peer
            # To get the block with current height, we need to fetch for blocks from
            # previous height
            blocks = peer.fetch_blocks_from_height(height - 1)
            for block in blocks:
                height_block_map[block.height] = block

        if height in height_block_map:
            is_valid = _is_valid_block(
                height_block_map[height], height, current_round, delegate_keys
            )
            if not is_valid:
                return False
        else:
            print(
                'Could not find block with height {} in mapping {}'.format(
                    height, height_block_map
                )
            )
            return False

    return True


def verify_peer_status(peer, body):
    """
    Verify the peer's blockchain (claimed state).
    Confirm that the peer's chain is either:
    - the same as ours or
    - different than ours but legit.
    Legit chain would have blocks signed/forged by the appropriate delegate(s).

    We distinguish 6 different cases with respect to our chain and peer's chain:

    Case1. Peer height > our height and our highest block is part of the peer's chain.
      This means the peer is ahead of us, on the same chain. No fork.
      We verify: his blocks that have height > our height (up to the round end).

    Case2. Peer height > our height and our highest block is not part of the peer's
      chain
      This means that the peer is on a different, higher chain. It has forked before our
      latest block.
      We verify: the first few of the peer's blocks after the fork (up to the round end)

    Case3. Peer height == our height and our latest blocks are the same.
      This means that our chains are the same.
      We verify: nothing.

    Case4. Peer height == our height and our latest blocks differ.
      This means that we are on a different chains with equal height. A fork has
      occurred
      We verify: the first few of the peer's blocks after the fork (up to the round end)

    Case5. Peer height < our height and peer's latest block is part of our chain.
      This means that the peer is on the same chain as us, just lagging behind.

    Case6. Peer height < our height and peer's latest block is not part of our chain.
      This means that we have forked and the peer's chain is lower.
      We verify: the first few of the peer's blocks after the fork (up to the round end)
    """
    database = load_plugin('chain.plugins.database')
    last_block = database.get_last_block()
    peer_height = int(body['header']['height'])
    peer_id = body['header']['id']

    """
    Case3. Peer height == our height and our latest blocks are the same.
      This means that our chains are the same.
    """
    if last_block.height == peer_height and last_block.id == peer_id:
        print(
            "Peer's latest block is the same as our latest block (height={}, id={}). Identical chains.".format(
                last_block.height, last_block.id
            )
        )
        return {
            'my_height': last_block.height,
            'his_height': peer_height,
            'highest_common_height': peer_height,
        }

    """
    Case5. Peer height < our height and peer's latest block is part of our chain.
      This means that the peer is on the same chain as us, just lagging behind.
    """
    if peer_height < last_block.height:
        blocks = database.get_blocks_by_heights([peer_height])
        block = blocks[0]
        if block.id == peer_id:
            return {
                'my_height': last_block.height,
                'his_height': peer_height,
                'highest_common_height': peer_height,
            }

    highest_common_height = _find_highest_common_block_height(
        peer, 1, min(peer_height, last_block.height)
    )
    if not highest_common_height:
        return None

    valid_peer_blocks = _verify_peer_blocks(
        peer, highest_common_height + 1, peer_height
    )
    if not valid_peer_blocks:
        return None

    return {
        'my_height': last_block.height,
        'his_height': peer_height,
        'highest_common_height': highest_common_height,
    }
