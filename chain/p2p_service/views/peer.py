from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.response import Response
from pyramid.view import view_config

from chain.crypto import slots, time
from chain.crypto.objects.block import Block
from chain.common.plugins import load_plugin


@view_config(route_name='peer_status', request_method='GET', renderer='json')
def status_get_view(request):
    # if request.method != 'GET':
    #     raise HTTPMethodNotAllowed(request.method)

    # TODO: This is REALLY bad, to connect to db on every request
    db = load_plugin('chain.plugins.database')

    last_block = db.get_last_block()

    return {
        'success': True,
        'height': last_block.height if last_block else 0,
        'forgingAllowed': slots.is_forging_allowed(last_block.height, time.get_time()),
        'currentSlot': slots.get_slot_number(last_block.height, time.get_time()),
        'header': last_block.get_header() if last_block else {},
    }


@view_config(route_name='peer_blocks', request_method='GET', renderer='json')
def block_get_view(request):
    # TODO: handle exceptions that can happen in this next line
    last_block_height = request.params.get('lastBlockHeight')

    # TODO: This is REALLY bad, to connect to db on every request
    db = load_plugin('chain.plugins.database')

    if last_block_height:
        # TODO: handle exception when failed to convert to int
        last_block_height = int(last_block_height) + 1
        blocks = db.get_blocks(last_block_height, 400)
    else:
        last_block = db.get_last_block()
        blocks = [last_block]
        last_block_height = last_block.height

    print('{} has downloaded {} blocks from height {}'.format(
        request.remote_addr,
        len(blocks),
        last_block_height
    ))

    return {
        'success': True,
        'blocks': [block.to_json() for block in blocks],
    }


@view_config(route_name='peer_blocks', request_method='POST', renderer='json')
def block_post_view(request):
    # if request.method != 'POST':
    #     raise HTTPMethodNotAllowed(request.method)

    # TODO: Wrap everything in try except

    # TODO: Validate request data that it's correct block structure
    block_data = request.json.get('block')
    if not block_data:
        raise Exception('There was no block in request to the /peer/blocks endpoint')

    block = Block.from_dict(block_data)
    print(
        'Received new block at height {} with {} transactions, from {}'.format(
            block.height,
            block.number_of_transactions,
            request.remote_addr,  # TODO: check if this works?
        )
    )

    # TODO: pingBlock
    # if (blockchain.pingBlock(block)) {
    #             return { success: true };
    #         }

    # TODO: check if we already got the block
    # const lastDownloadedBlock = blockchain.getLastDownloadedBlock();

    # // Are we ready to get it?
    # if (lastDownloadedBlock && lastDownloadedBlock.data.height + 1 !== block.height) {
    #     return { success: true };
    # }

    is_verified, errors = block.verify()
    if not is_verified:
        print(errors)  # TODO:
        return {'success': False}

    # blockchain.pushPingBlock(b.data);
    # block.ip = request.info.remoteAddress;

    queue = load_plugin('chain.plugins.process_queue')
    queue.push_block(block)

    return {'success': True}


@view_config(route_name='peer_transactions', request_method='GET', renderer='json')
def transaction_get_view(request):
    # if request.method not in ['GET', 'POST']:
    #     raise HTTPMethodNotAllowed(request.method)
    return {
        'success': True,
        'transactions': [],
    }


@view_config(route_name='peer_transactions', request_method='POST', renderer='json')
def transaction_post_view(request):
    return {
        'success': False,
        'message': 'Transaction pool not available'
    }
    # TODO: implement the rest of this function with transaction pool an stuffz


@view_config(route_name='peer_common_blocks', request_method='GET', renderer='json')
def common_blocks_view(request):
    param_ids = request.params.get('ids', '').split(',')[:9]
    block_ids = []
    for block_id in param_ids:
        # Skip all IDs that can't be converted to int
        try:
            int(block_id)
        except ValueError:
            continue
        # We don't convert block_ids to integers as the whole codebase is using
        # block ids as strings
        block_ids.append(block_id)

    # TODO: This is REALLY bad, to connect to db on every request
    db = load_plugin('chain.plugins.database')
    last_block = db.get_last_block()
    if block_ids:
        common_blocks = db.get_blocks_by_id(block_ids)
        common = None
        if common_blocks:
            block = common_blocks[0]
            common = {
                'id': block.id,
                'height': block.height,
                'timestamp': block.timestamp,
                'previousBlock': block.previous_block,
            }
        return {
            'success': True,
            'common': common,
            'lastBlockHeight': last_block.height,
        }
    else:
        return {
            'success': True,
            'common': None,
            'lastBlockHeight': last_block.height,
        }


# @view_config(route_name='peer_list', request_method='GET', renderer='json')
# def peers_get_view(request):
#     peer_manager = load_plugin('chain.plugins.peers')
#     # TODO: order peers by delay?
#     peers = peer_manager.peers
    





