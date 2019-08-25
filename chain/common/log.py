import sys

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": (
                "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
        }
    },
    "loggers": {
        "peewee": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "websockets": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "asyncio": {"propagate": False, "level": "WARNING", "handlers": ["console"]},
        "chain.p2p.socket_protocol": {
            "propagate": False,
            "level": "WARNING",
            "handlers": ["console"],
        },
        "": {"handlers": ["console"], "level": "DEBUG"},
    },
}
