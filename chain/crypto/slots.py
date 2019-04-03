import math

from chain.common.config import config

# TODO: move this to utils or someting and out of crypto?


def get_slot_number(height, epoch_time):
    # TODO: find a better way to get milestone data
    milestone = config.get_milestone(height)
    return math.floor(epoch_time / milestone["blocktime"])


def is_forging_allowed(height, epoch_time):
    milestone = config.get_milestone(height)
    return epoch_time % milestone["blocktime"] < milestone["blocktime"] / 2
