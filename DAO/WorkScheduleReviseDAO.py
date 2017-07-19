import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkScheduleReviseDAO:

    @classmethod
    def update_or_create_task_events(cls):
        pass

    @classmethod
    def update_or_create_avail_events(cls):

        pass

    @classmethod
    def update_or_create_time_off_events(cls):
        pass