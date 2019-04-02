import os

from redis import Redis

from chain.config import Config


class Queue(object):

    list_name = "process_queue"
    restored_database_integrity = False
    forging_delegates = []

    def __init__(self):
        super().__init__()

        self.db = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
        )

    def push_block(self, block):
        serialized_block = block.serialize_full()
        self.db.rpush(self.list_name, serialized_block)

    def pop_block(self):
        return self.db.lpop(self.list_name)

    def block_exists(self, block):
        key = "process_queue:block:{}:{}".format(block.height, block.id)

        if self.db.exists(key):
            self.db.incr(key)
            return True
        else:
            config = Config()
            blocktime = config.get_milestone(block.height)["blocktime"]
            # Expire the key after `blocktime` seconds
            self.db.set(key, 0, ex=blocktime)
            return False

    def clear(self):
        print("Clearing process queue")
        self.db.delete(self.list_name)
