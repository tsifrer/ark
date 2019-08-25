from chain.blockchain.utils import is_block_chained
from chain.common.config import config
from chain.common.plugins import load_plugin
from chain.common.utils import get_chain_version
from chain.crypto import slots, time
from chain.crypto.objects.block import Block


class Handlers(object):
    def __init__(self):
        super().__init__()
        self.db = load_plugin("chain.plugins.database")
        self.process_queue = load_plugin("chain.plugins.process_queue")
        self.transaction_pool = load_plugin("chain.plugins.transaction_pool")

    @property
    def socket(self):
        if self._socket:
            return self._socket
        raise Exception("Socket is not set")

    def set_socket(self, socket):
        self._socket = socket

    async def get_last_block(self):
        last_block = self.db.get_last_block()
        return last_block

    async def get_blocks(self, data):
        self.socket.log_info(data)
        block_height = int(data["lastBlockHeight"]) + 1
        block_limit = int(data.get("blockLimit") or 400)
        headers_only = data.get("headersOnly") or False
        serialized = data.get("serialized") or False

        blocks = self.db.get_blocks(
            block_height, block_limit, serialized, not headers_only
        )
        return [block.to_json() for block in blocks]

    async def get_common_blocks(self, data):
        self.socket.log_info(data)
        ids = data["ids"]
        last_block = self.db.get_last_block()
        if ids:
            common_blocks = self.db.get_blocks_by_id(ids)
            common = None
            if common_blocks:
                block = common_blocks[0]
                common = {
                    "id": block.id,
                    "height": block.height,
                    "timestamp": block.timestamp,
                    "previousBlock": block.previous_block,
                }
            data = {"common": common, "lastBlockHeight": last_block.height}
        else:
            data = {"common": None, "lastBlockHeight": last_block.height}
        return data

    async def get_status(self):
        last_block = self.db.get_last_block()
        return {
            "state": {
                "height": last_block.height if last_block else 0,
                "forgingAllowed": slots.is_forging_allowed(
                    last_block.height, time.get_time()
                ),
                "currentSlot": slots.get_slot_number(
                    last_block.height, time.get_time()
                ),
                "header": last_block.get_header() if last_block else {},
            },
            "config": {
                "version": get_chain_version(),
                "network": {
                    "version": config.network["pubKeyHash"],
                    "name": config.network["name"],
                    "nethash": config.network["nethash"],
                    "explorer": config.network["client"]["explorer"],
                    "token": {
                        "name": config.network["client"]["token"],
                        "symbol": config.network["client"]["symbol"],
                    },
                },
            },
        }

    async def post_block(self, data, ip):
        # TODO: Wrap everything in try except

        # TODO: Validate request data that it's correct block structure
        block_data = data["block"]
        # if not block_data:
        #     raise Exception(
        #         "There was no block in request to the /peer/blocks endpoint"
        #     )

        block = Block.from_dict(block_data)
        self.socket.log_info(
            "Received new block at height %s with %s transactions, from %s",
            block.height,
            block.number_of_transactions,
            ip,
        )

        is_verified, errors = block.verify()
        if not is_verified:
            self.socket.log_error(errors)  # TODO:
            raise Exception("Verification failed")

        last_block = self.db.get_last_block()

        if last_block.height >= block.height:
            self.socket.log_info(
                "Received block with height %s which was already processed. Our last "
                "block height %s. Skipping process queue.",
                block.height,
                last_block.height,
            )
            return

        if self.process_queue.block_exists(block):
            self.socket.log_info(
                "Received block with height %s is already in process queue.",
                block.height,
            )
            return

        current_slot = slots.get_slot_number(last_block.height, time.get_time())
        received_slot = slots.get_slot_number(last_block.height, block.timestamp)

        if current_slot >= received_slot and is_block_chained(last_block, block):
            # Put the block to process queue
            self.process_queue.push_block(block)
        else:
            self.socket.log_info(
                "Discarded block %s because it takes a future slot", block.height
            )

    async def post_transactions(self, data, ip):
        # TODO: Wrap everything in try except
        transactions_data = data.get("transactions")
        result = self.transaction_pool.process_transactions(transactions_data)
        self.socket.log_info("Result of process_transactions: %s", result)
        if len(result["invalid"]) > 0:
            # TODO: exception?
            raise Exception("There was an error with one or more transactions")
        return result["accepted"]
