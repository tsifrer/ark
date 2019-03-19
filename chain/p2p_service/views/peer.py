from flask import jsonify, request, current_app
from flask.views import MethodView

from chain.common.plugins import load_plugin
from chain.crypto import slots, time
from chain.crypto.objects.block import Block

from ..exceptions import P2PException

from ..external import get_db

from flask import Blueprint

class PeerView(MethodView):
    def get(self):
        db = get_db()
        last_block = db.get_last_block()
        data = {
            'success': True,
            'height': last_block.height if last_block else 0,
            'forgingAllowed': slots.is_forging_allowed(last_block.height, time.get_time()),
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

        print('{} has downloaded {} blocks from height {}'.format(
            request.remote_addr,
            len(blocks),
            last_block_height
        ))

        data = {
            'success': True,
            'blocks': [block.to_json() for block in blocks],
        }
        return jsonify(data), 200

    def post(self):
        # TODO: Wrap everything in try except

        # TODO: Validate request data that it's correct block structure
        block_data = request.get_json().get('block')
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
            raise P2PException('Verification failed')

        queue = load_plugin('chain.plugins.process_queue')
        queue.push_block(block)

        return jsonify({'success': True}), 200


class TransactionView(MethodView):
    def get(self):
        data = {
            'success': True,
            'transactions': [],
        }
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
    print(request.path)
    # required_headers = ['version', 'nethash', 'port', 'os']

    ip = request.remote_addr

    # TODO:

def blueprint():
    bp = Blueprint('peer', __name__)

    bp.before_request(_accept_new_peer_on_request)

    bp.add_url_rule('/status', view_func=PeerView.as_view('peer'))
    bp.add_url_rule('/blocks', view_func=BlockView.as_view('block'))
    bp.add_url_rule('/blocks/common', view_func=BlockCommonView.as_view('block_common'))
    bp.add_url_rule('/transactions', view_func=TransactionView.as_view('transaction'))
    return bp
