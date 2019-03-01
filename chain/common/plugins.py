# TODO rename this module
import inspect
from importlib import import_module

from chain.common.interfaces import IPlugin


# INSTALLED_PLUGINS = [
#     'chain.plugins.database',
# ]


# PLUGINS = {}


def load_plugin(app, plugin):
    module = import_module(plugin)
    for attr in dir(module):
        obj = getattr(module, attr)
        if attr != 'IPlugin' and inspect.isclass(obj) and issubclass(obj, IPlugin):
            plugin = obj()
            return plugin.register(app)


# def load_plugins(app, plugins):
#     loaded_plugins = {}
#     for module in plugins:
#         module = import_module(module)
#         for attr in dir(module):
#             obj = getattr(module, attr)
#             if attr != 'IPlugin' and inspect.isclass(obj) and issubclass(obj, IPlugin):
#                 plugin = obj()
#                 name = getattr(plugin, 'name', None)
#                 if not name:
#                     raise Exception(
#                         'Pluigin is missing a name'
#                     )  # TODO: improve this exception

#                 loaded_plugins[plugin.name] = plugin.register(app)

#     return loaded_plugins
