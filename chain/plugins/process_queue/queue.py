from redis import Redis


class Queue(object):

    list_name = 'process_queue'
    restored_database_integrity = False
    forging_delegates = []

    def __init__(self, app):
        super().__init__()
        self.app = app

        self.db = Redis(host='localhost', port=6379, db=0)

    def push_block(self, block):
        serialized_block = block.serialize_full()
        self.db.rpush(self.list_name, serialized_block)

    def pop_block(self):
        return self.db.lpop(self.list_name)
