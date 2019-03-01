import math

from chain.config import Config

# TODO: move this to utils or someting and out of crypto?


def get_slot_number(height, epoch_time):
    # TODO: find a better way to get milestone data
    config = Config()
    milestone = config.get_milestone(height)
    return math.floor(epoch_time / milestone['blocktime'])
