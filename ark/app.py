from ark.config import Config
from ark.settings import load_plugins
from ark.crypto.time import Time

class App(object):
    _config = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        load_plugins(self)

        self.time = Time()

    @property
    def config(self):
        if not self._config:
            # self._config = get_config()
            self._config = Config()
        return self._config
