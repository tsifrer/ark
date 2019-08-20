from chain.blockchain.utils import is_block_chained
from chain.common.config import config
from chain.common.plugins import load_plugin
from chain.common.utils import get_chain_version
from chain.crypto import slots, time
from chain.crypto.objects.block import Block


class Handlers(object):
    def __init__(self):
        super().__init__()
        print("WEBSOCKET HANDLER INITIALIZED")
        self.db = load_plugin("chain.plugins.database")
        self.process_queue = load_plugin("chain.plugins.process_queue")
        self.transaction_pool = load_plugin("chain.plugins.transaction_pool")

    async def get_last_block(self):
        last_block = self.db.get_last_block()
        return last_block

    async def get_blocks(self, data):
        print(data)
        block_height = int(data["lastBlockHeight"]) + 1
        block_limit = int(data.get("blockLimit") or 400)
        headers_only = data.get("headersOnly") or False
        serialized = data.get("serialized") or False

        blocks = self.db.get_blocks(
            block_height, block_limit, serialized, not headers_only
        )
        return [block.to_json() for block in blocks]

    async def get_common_blocks(self, data):
        print(data)
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
        print(
            "Received new block at height {} with {} transactions, from {}".format(
                block.height, block.number_of_transactions, ip
            )
        )

        is_verified, errors = block.verify()
        if not is_verified:
            print(errors)  # TODO:
            raise Exception("Verification failed")

        last_block = self.db.get_last_block()

        if last_block.height >= block.height:
            print(
                "Received block with height {} which was already processed. Our last "
                "block height {}. Skipping process queue.".format(
                    block.height, last_block.height
                )
            )
            return

        if self.process_queue.block_exists(block):
            print(
                "Received block with height {} is already in process queue.".format(
                    block.height
                )
            )
            return

        current_slot = slots.get_slot_number(last_block.height, time.get_time())
        received_slot = slots.get_slot_number(last_block.height, block.timestamp)

        if current_slot >= received_slot and is_block_chained(last_block, block):
            # Put the block to process queue
            self.process_queue.push_block(block)
        else:
            print(
                "Discarded block {} because it takes a future slot".format(block.height)
            )

    async def post_transactions(self, data, ip):
        # TODO: Wrap everything in try except
        transactions_data = data.get("transactions")
        result = self.transaction_pool.process_transactions(transactions_data)
        print("Result of process_transactions", result)
        if len(result["invalid"]) > 0:
            # TODO: exception?
            raise Exception("There was an error with one or more transactions")
        return result["accepted"]
