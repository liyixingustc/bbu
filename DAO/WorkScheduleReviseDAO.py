import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkScheduleReviseDAO:
    pass