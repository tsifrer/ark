from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.response import Response
from pyramid.view import view_config

from chain.crypto import slots, time
from chain.crypto.objects.block import Block
from chain.plugins.database.database import Database
from chain.plugins.process_queue.queue import Queue


@view_config(route_name='status', renderer='json')
def status(request):
    if request.method != 'GET':
        raise HTTPMethodNotAllowed(request.method)

    # TODO: This is REALLY bad, to connect to db on every request
    db = Database(None)

    last_block = db.get_last_block()

    return {
        'success': True,
        'height': last_block.height if last_block else 0,
        'forgingAllowed': slots.is_forging_allowed(last_block.height, time.get_time()),
        'currentSlot': slots.get_slot_number(last_block.height, time.get_time()),
        'header': last_block.get_header() if last_block else {},
    }


@view_config(route_name='peer_block_view', renderer='json')
def peer_block_view(request):
    if request.method != 'POST':
        raise HTTPMethodNotAllowed(request.method)

    # TODO: Wrap everything in try except

    # TODO: Validate request data that it's correct block structure
    block_data = request.json.get('block')
    if not block_data:
        raise
    block = Block.from_dict(block_data)

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

    queue = Queue(None)
    queue.push_block(block)
    return {'success': True}


@view_config(route_name='block_store', renderer='json')
def block_store_view(request):
    if request.method != 'POST':
        raise HTTPMethodNotAllowed(request.method)

    # TODO: Validate request data that it's correct block structure

    # TODO: after validation you should not need this
    block_data = request.json.get('block')
    if not block_data:
        raise
    block = Block.from_dict(block_data)
    print(
        'Received new block at height {} with {} transactions, from {}'.format(
            block.height,
            block.number_of_transactions,
            request.remote_addr,  # TODO: check if this works?
        )
    )

    # TODO: This is REALLY bad, to connect to db on every request
    db = Database(None)

    last_block = db.get_last_block()
    current_slot = slots.get_slot_number(last_block.height, time.get_time())

    received_slot = slots.get_slot_number(block.height, block.timestamp)
    print(current_slot)
    print(received_slot)

    if received_slot <= current_slot:

        # TODO: if blockchain.state.started and blockchain.state == 'idle'

        # TODO: This is REALLY bad, to connect to redis on every request
        queue = Queue(None)
        queue.push_block(block)

        # else:
        #     print('Block disregarded because blockchain is not ready')
        pass
    else:
        print('Discarded block {} because it takes a future slot'.format(block.height))

    return Response(status=204)
