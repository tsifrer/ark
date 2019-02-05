from ark.config import Config
from ark.crypto.time import Time
from ark.settings import load_plugins


class App(object):
    _config = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = Time(self)
        self.version = '0.0.1'

        load_plugins(self)

    @property
    def config(self):
        if not self._config:
            # self._config = get_config()
            self._config = Config()
        return self._config
