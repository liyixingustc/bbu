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

    @classmethod
    def now_local(cls):
        return cls.local_tz.localize(datetime.now())

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
        behind = cls.local_tz.localize(datetime(date.year, date.month, date.day) + timedelta(days=1)) - date
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

    @classmethod
    def remove_overlap(cls, r1_start, r1_end, r2_start, r2_end):

        r1_start = r1_start.astimezone(cls.local_tz)
        r1_end = r1_end.astimezone(cls.local_tz)
        r2_start = r2_start.astimezone(cls.local_tz)
        r2_end = r2_end.astimezone(cls.local_tz)

        latest_start = max(r1_start, r2_start)
        earliest_end = min(r1_end, r2_end)

        if latest_start == r1_start and earliest_end == r1_end:
            return [[r1_start, r1_start]]
        elif latest_start == r1_start and earliest_end < r1_end:
            return [[earliest_end, r1_end]]
        elif earliest_end == r1_end and latest_start > r1_start:
            return [[r1_start, latest_start]]
        elif latest_start > r1_start and earliest_end < r1_end:
            return [[r1_start, latest_start], [earliest_end, r1_end]]
        else:
            return []

    mapping = {'3': 1, '1': 2, '2': 3}
    reverse_mapping = {1: '3', 2: '1', 3: '2'}

    @classmethod
    def pick_shift_by_start_shift(cls, start_shift):
        shift_range = range(cls.mapping[start_shift], 3 + 1)
        return shift_range

    @classmethod
    def pick_shift_by_end_shift(cls, end_shift):
        shift_range = range(1, cls.mapping[end_shift] + 1)
        return shift_range

    @classmethod
    def pick_shift_by_two_shift(cls, start_shift, end_shift):

        if cls.mapping[end_shift] > cls.mapping[start_shift]:
            shift_range = range(cls.mapping[start_shift], cls.mapping[end_shift] + 1)
            shift_range = list(map(lambda x: cls.reverse_mapping[x], shift_range))
        else:
            shift_range = [start_shift]
        return shift_range

