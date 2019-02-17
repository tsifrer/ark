import math
from datetime import datetime

from dateutil.parser import isoparse
from dateutil.tz import tzutc, UTC

from ark.config import Config

# TODO: move this to utils or someting and out of crypto?


def get_epoch_time():
    # TODO: Might be better to use `get_milestone` from the config, but then
    # we need to figure out how to pass/store the height
    config = Config()
    date = isoparse(config['milestones'][0]['epoch'])
    return date.astimezone(UTC)


def get_time(time=None):
    if not time:
        time = datetime.now(tzutc())

    start = get_epoch_time()
    return math.floor((time - start).total_seconds())


def get_real_time(epoch_time=None):
    if not epoch_time:
        epoch_time = get_time()
    start = get_epoch_time().timestamp()
    return math.floor(start + epoch_time)
