import datetime as dt
import time
import calendar
import pytz
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse
from tzlocal import get_localzone


class UDatetime:

    local_tz = get_localzone()

    def __init__(self):
        pass

    @property
    def now_local(self):
        return datetime.now(tz=self.local_tz)

    @classmethod
    def to_local(cls, date):
        return date.astimezone(tz=cls.local_tz)

    @classmethod
    def datetime_str_init(cls, timestamp,
                          default_base=dt.datetime.now(),
                          default_delta=timedelta(days=0)):
        if timestamp:
            timestamp = parse(timestamp)
            if not timestamp.tzinfo:
                timestamp = cls.local_tz.localize(timestamp)
        else:
            timestamp = default_base + default_delta

        return timestamp

    @staticmethod
    def check_date(start, end):
        if start.date() == end.date():
            return start.date()
        elif start.date() + timedelta(days=1) == end.date():
            middle = datetime(start.year, start.month, start.day+1, 0, 0)
            ahead = middle - start
            behind = end - middle
            if behind >= ahead:
                return end.date()
            else:
                return start.date()
        else:
            return start.date() + timedelta(days=1)

    @staticmethod
    def get_overlap(r1_start, r1_end, r2_start, r2_end):
        latest_start = max(r1_start, r1_end)
        earliest_end = min(r2_start, r2_end)
        delta = (earliest_end - latest_start).total_seconds()/3600
        if delta > 0:
            return delta
        else:
            return 0
