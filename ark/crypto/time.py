import math
from datetime import datetime
from dateutil.tz import tzutc
from dateutil.parser import parse

# TODO: move this to utils or someting
class Time(object):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def get_epoch_time(self):
        # TODO: Might be better to use `get_milestone` from the config, but then
        # we need to figure out how to pass/store the height
        return parse(self.app.config['milestones'][0]['epoch'])

    def get_time(self, time=None):
        if not time:
            time = datetime.now(tzutc())

        start = self.get_epoch_time()
        return math.floor((time - start).total_seconds())
