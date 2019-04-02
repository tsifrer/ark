from chain.common.interfaces import IPlugin

from .queue import Queue


class Plugin(IPlugin):
    name = "process_queue"

    def register(self):
        return Queue()
