import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

from DAO.WorkScheduleDataDAO import WorkScheduleDataDAO

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

    @classmethod
    def update_or_create_schedule(cls, user, start, end, date, est, avail_id, worker, task):

        WorkerScheduled.objects.update_or_create(name=worker,
                                                 date=date,
                                                 task_id=task,
                                                 available_id=avail_id,
                                                 defaults={
                                                     'created_by': user,
                                                     'duration': est,
                                                     'time_start': start,
                                                     'time_end': end,
                                                     'source': 'auto',
                                                 })
        scheduled_hour = WorkScheduleDataDAO.get_schedule_hour_by_task_id(task.id)

        Tasks.objects.filter(id=task.id).update(current_status='Scheduled',
                                                scheduled_hour=scheduled_hour)
