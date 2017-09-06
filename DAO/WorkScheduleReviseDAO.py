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
    def update_or_create_schedule(cls, user, start, end, date, duration, avail_id, worker, task):

        WorkerScheduled.objects.update_or_create(name=worker,
                                                 date=date,
                                                 task_id=task,
                                                 available_id=avail_id,
                                                 defaults={
                                                     'created_by': user,
                                                     'duration': duration,
                                                     'time_start': start,
                                                     'time_end': end,
                                                     'source': 'auto',
                                                 })
        scheduled_hour = WorkScheduleDataDAO.get_schedule_hour_by_task_id(task.id)

        Tasks.objects.filter(id=task.id).update(current_status='Scheduled',
                                                scheduled_hour=scheduled_hour)

    @classmethod
    def remove_schedule_by_id(cls, schedule_id):
        schedule_obj = WorkerScheduled.objects.filter(id__exact=schedule_id)
        if schedule_obj.exists():
            task_id = schedule_obj[0].task_id.id
            scheduld_hour = WorkScheduleDataDAO.get_schedule_hour_by_task_id(task_id)
            Tasks.objects.filter(id__exact=task_id).update(current_status='Work Request',
                                                           scheduled_hour=scheduld_hour)
            WorkerScheduled.objects.filter(id__exact=schedule_id).delete()

        return True

    @classmethod
    def remove_schedule_by_date_range_and_worker(cls, start, end, worker):
        schedules = WorkerScheduled.objects.filter(date__range=[start, end],
                                                   name__exact=worker)
        for schedule in schedules:
            cls.remove_schedule_by_id(schedule.id)

        return True

    @classmethod
    def remove_available_by_id(cls, available_id):
        available_obj = WorkerAvailable.objects.filter(id__exact=available_id)
        if available_obj.exists():
            WorkerAvailable.objects.filter(id__exact=available_id).delete()

        return True

    @classmethod
    def remove_available_by_date_range_and_worker(cls, start, end, worker):
        availables = WorkerAvailable.objects.filter(date__range=[start, end],
                                                    name__exact=worker)

        for available in availables:
            cls.remove_available_by_id(available.id)

        return True