from flask import jsonify, request, current_app
from flask.views import MethodView

from chain.crypto import slots, time
from chain.crypto.objects.block import Block
from chain.plugins.peers.tasks import add_peer
from chain.plugins.peers.utils import ip_is_blacklisted

from ..exceptions import P2PException

from ..external import get_db, get_peer_manager, get_process_queue

from flask import Blueprint


class PeerView(MethodView):
    def get(self):
        db = get_db()
        last_block = db.get_last_block()
        data = {
            'success': True,
            'height': last_block.height if last_block else 0,
            'forgingAllowed': slots.is_forging_allowed(
                last_block.height, time.get_time()
            ),
            'currentSlot': slots.get_slot_number(last_block.height, time.get_time()),
            'header': last_block.get_header() if last_block else {},
        }
        return jsonify(data), 200


class BlockView(MethodView):
    def get(self):
        # TODO: handle exceptions that can happen in this next line
        last_block_height = request.args.get('lastBlockHeight')

        db = get_db()
        if last_block_height:
            # TODO: handle exception when failed to convert to int
            last_block_height = int(last_block_height) + 1
            blocks = db.get_blocks(last_block_height, 400)
        else:
            last_block = db.get_last_block()
            blocks = [last_block]
            last_block_height = last_block.height

        print(
            '{} has downloaded {} blocks from height {}'.format(
                request.remote_addr, len(blocks), last_block_height
            )
        )

        data = {'success': True, 'blocks': [block.to_json() for block in blocks]}
        return jsonify(data), 200

    def post(self):
        # TODO: Wrap everything in try except

        # TODO: Validate request data that it's correct block structure
        block_data = request.get_json().get('block')
        if not block_data:
            raise Exception(
                'There was no block in request to the /peer/blocks endpoint'
            )

        block = Block.from_dict(block_data)
        print(
            'Received new block at height {} with {} transactions, from {}'.format(
                block.height,
                block.number_of_transactions,
                request.remote_addr,  # TODO: check if this works?
            )
        )

        is_verified, errors = block.verify()
        if not is_verified:
            print(errors)  # TODO:
            raise P2PException('Verification failed')

        db = get_db()
        last_block = db.get_last_block()

        if last_block.height >= block.height:
            print(
                'Received block with height {} which was already processed. Our last block height {}. Skipping process queue.'.format(
                    block.height, last_block.height
                )
            )
            return jsonify({'success': True}), 200

        process_queue = get_process_queue()

        if process_queue.block_exists(block):
            print(
                'Received block with height {} is already in process queue.'.format(
                    block.height
                )
            )
            return jsonify({'success': True}), 200

        current_slot = slots.get_slot_number(last_block.height, time.get_time())
        received_slot = slots.get_slot_number(last_block.height, block.timestamp)

        if current_slot >= received_slot:
            # Put the block to process queue
            process_queue.push_block(block)
        else:
            print(
                'Discarded block {} because it takes a future slot'.format(block.height)
            )

        return jsonify({'success': True}), 200


class TransactionView(MethodView):
    def get(self):
        data = {'success': True, 'transactions': []}
        return jsonify(data), 200

    def post(self):
        raise P2PException('Transaction pool not available', status_code=404)
        # TODO: implement the rest of this function with transaction pool an stuffz


class BlockCommonView(MethodView):
    def get(self):
        param_ids = request.args.get('ids', '').split(',')[:9]
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
        db = get_db()
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
            data = {
                'success': True,
                'common': common,
                'lastBlockHeight': last_block.height,
            }
        else:
            data = {
                'success': True,
                'common': None,
                'lastBlockHeight': last_block.height,
            }
        return jsonify(data), 200


# # @view_config(route_name='peer_list', request_method='GET', renderer='json')
# # def peers_get_view(request):
# #     peer_manager = load_plugin('chain.plugins.peers')
# #     # TODO: order peers by delay?
# #     peers = peer_manager.peers


def _accept_new_peer_on_request():
    peer_manager = get_peer_manager()
    ip = request.remote_addr
    # TODO: improve how we check if the peer exists in redis
    # Don't try and add a peer if it's blacklisted or if it already is our peer
    if not ip_is_blacklisted(ip) and not peer_manager.peer_with_ip_exists(ip):
        add_peer(
            ip=ip,
            port=request.headers['port'],
            chain_version=request.headers['version'],
            nethash=request.headers['nethash'],
            os=request.headers.get('os'),
        )


def blueprint():
    bp = Blueprint('peer', __name__)

    # TODO: Disable this if peer discoverability is disabled in config
    bp.before_request(_accept_new_peer_on_request)

    bp.add_url_rule('/status', view_func=PeerView.as_view('peer'))
    bp.add_url_rule('/blocks', view_func=BlockView.as_view('block'))
    bp.add_url_rule('/blocks/common', view_func=BlockCommonView.as_view('block_common'))
    bp.add_url_rule('/transactions', view_func=TransactionView.as_view('transaction'))
    return bp
