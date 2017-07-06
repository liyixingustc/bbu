import datetime as dt
import time
import calendar
import pytz
from datetime import datetime, timedelta
from dateutil import parser, tz


class UDatetime:

    locoal_tz = tz.tzlocal()

    def __init__(self):
        pass

    @property
    def now_local(self):
        return datetime.now(tz=tz.tzlocal())

    @staticmethod
    def to_local(date):
        return date.astimezone(tz=tz.tzlocal())

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
