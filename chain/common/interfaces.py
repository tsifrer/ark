import abc


class IPlugin(abc.ABC):
    def register(self):
        pass

    def deregister(self):
        pass
