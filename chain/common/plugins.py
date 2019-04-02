# TODO rename this module
import inspect
from importlib import import_module

from chain.common.interfaces import IPlugin


def load_plugin(plugin):
    module = import_module(plugin)
    for attr in dir(module):
        obj = getattr(module, attr)
        if attr != "IPlugin" and inspect.isclass(obj) and issubclass(obj, IPlugin):
            plugin = obj()
            return plugin.register()
