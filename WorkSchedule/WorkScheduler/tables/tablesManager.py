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
    def set_data(cls):
        tasks = WorkScheduleDataDAO.get_all_tasks_scheduled()

        return tasks
