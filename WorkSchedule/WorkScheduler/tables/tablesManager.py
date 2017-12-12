import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

# from ..models.models import *
from ...WorkConfig.models import *
from ...WorkWorkers.models.models import *

from DAO.WorkScheduleDataDAO import WorkScheduleDataDAO


class WorkSchedulerPanel2Table1Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, pagination=False, page_size=None, offset=None, filter=None, sort=None, order=None):
        tasks = WorkScheduleDataDAO.get_all_tasks_open(pagination, page_size, offset, filter, sort, order)

        return tasks
