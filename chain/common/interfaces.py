import abc


class IPlugin(abc.ABC):
    # @property
    # @abc.abstractmethod
    # def name(self):
    #     pass

    # @property
    # def x(self):
    #     ...

    # @x.setter
    # @abc.abstractmethod
    # def x(self, val):
    #     print(val)

    def register(self):
        pass

    def deregister(self):
        pass
