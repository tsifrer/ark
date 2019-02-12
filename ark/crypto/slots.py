import math
from datetime import datetime
from dateutil.tz import tzutc
from dateutil.parser import parse

# TODO: move this to utils or someting and out of crypto?
class Slots(object):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def get_slot_number(self, height, epoch_time):
        milestone = self.app.config.get_milestone(height)
        return math.floor(epoch_time / milestone['blocktime'])
