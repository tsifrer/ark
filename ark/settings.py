import inspect
from importlib import import_module

from ark.interfaces.plugin import IPlugin


INSTALLED_PLUGINS = [
    'ark.plugins.database_peewee',
    'ark.plugins.blockchain',
]


PLUGINS = {}


def load_plugins(app):
    for module in INSTALLED_PLUGINS:
        module = import_module(module)
        for attr in dir(module):
            obj = getattr(module, attr)
            if attr != 'IPlugin' and inspect.isclass(obj) and issubclass(obj, IPlugin):
                plugin = obj()
                name = getattr(plugin, 'name', None)
                if not name:
                    raise Exception('Pluigin is missing a name')  # TODO: improve this exception

                PLUGINS[plugin.name] = plugin.register(app)
