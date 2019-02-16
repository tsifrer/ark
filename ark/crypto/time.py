import math
from datetime import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc

from ark.config import Config

# TODO: move this to utils or someting and out of crypto?


def get_epoch_time():
    # TODO: Might be better to use `get_milestone` from the config, but then
    # we need to figure out how to pass/store the height
    config = Config()
    return parse(config['milestones'][0]['epoch'])


def get_time(time=None):
    if not time:
        time = datetime.now(tzutc())

    start = get_epoch_time()
    return math.floor((time - start).total_seconds())
