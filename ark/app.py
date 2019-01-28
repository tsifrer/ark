from ark.config import get_config
from ark.settings import load_plugins


class App(object):
    _config = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        load_plugins(self)

    @property
    def config(self):
        if not self._config:
            self._config = get_config()
        return self._config
