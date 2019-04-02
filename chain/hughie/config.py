import os

from huey import RedisHuey

# TODO: config yo
huey = RedisHuey(
    "hughie",
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=os.environ.get("REDIS_PORT", 6379),
    db=os.environ.get("REDIS_DB", 0),
)
