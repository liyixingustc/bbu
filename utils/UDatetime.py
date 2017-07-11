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

    @classmethod
    def pick_date_by_one_date(cls, date):

        ahead = date - cls.local_tz.localize(datetime(date.year, date.month, date.day))
        behind = cls.local_tz.localize(datetime(date.year, date.month, date.day+1)) - date
        if ahead.total_seconds() >= behind.total_seconds() and behind.total_seconds() <= (3600*6):
            picked_date = (date + timedelta(days=1)).date()
        elif ahead.total_seconds() < behind.total_seconds() and ahead.total_seconds() <= (3600*6):
            picked_date = (date - timedelta(days=1)).date()
        else:
            picked_date = date.date()
        return picked_date

    @classmethod
    def pick_date_by_two_date(cls, start, end):
        if start.date() == end.date():
            return start.date()
        elif start.date() + timedelta(days=1) == end.date():
            middle = cls.local_tz.localize(datetime(start.year, start.month, start.day+1))
            ahead = middle - start
            behind = end - middle
            if behind >= ahead:
                return end.date()
            else:
                return start.date()
        else:
            return start.date() + timedelta(days=1)

    @classmethod
    def get_overlap(cls, r1_start, r1_end, r2_start, r2_end):

        r1_start = r1_start.astimezone(cls.local_tz)
        r1_end = r1_end.astimezone(cls.local_tz)
        r2_start = r2_start.astimezone(cls.local_tz)
        r2_end = r2_end.astimezone(cls.local_tz)

        latest_start = max(r1_start, r2_start)
        earliest_end = min(r1_end, r2_end)

        delta = earliest_end - latest_start

        if delta.total_seconds() > 0:
            return delta
        else:
            return timedelta(hours=0)
