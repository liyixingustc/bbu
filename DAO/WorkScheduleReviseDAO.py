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

    # sync by id
    @classmethod
    def sync_task_by_id(cls, task_id, current_status):
        scheduled_hour_by_task_id = WorkScheduleDataDAO.get_schedule_hour_by_task_id(task_id)
        Tasks.objects.filter(id=task_id).update(current_status=current_status,
                                                scheduled_hour=scheduled_hour_by_task_id)
        return True

    @classmethod
    def sync_avail_by_id(cls, available_id):
        schedule_hour_by_available_id = WorkScheduleDataDAO.get_schedule_hour_by_available_id(available_id)
        available = WorkerAvailable.objects.get(id=available_id)
        balance = available.duration - schedule_hour_by_available_id
        WorkerAvailable.objects.filter(id=available_id).update(balance=balance)
        return True

    # remove by id
    @classmethod
    def remove_schedule_by_id(cls, schedule_id):
        schedule_obj = WorkerScheduled.objects.filter(id__exact=schedule_id)
        if schedule_obj.exists():
            task_id = schedule_obj[0].task_id.id
            available_id = schedule_obj[0].available_id.id
            WorkerScheduled.objects.filter(id__exact=schedule_id).delete()
            cls.sync_task_by_id(task_id, 'Work Request')
            cls.sync_avail_by_id(available_id)
        return True

    @classmethod
    def remove_available_by_id(cls, available_id):
        available_obj = WorkerAvailable.objects.filter(id__exact=available_id)
        if available_obj.exists():
            WorkerAvailable.objects.filter(id__exact=available_id).delete()
        return True

    @classmethod
    def remove_task_by_id(cls, task_id):
        task_obj = Tasks.objects.filter(id__exact=task_id)
        if task_obj.exists():
            Tasks.objects.filter(id__exact=task_id).delete()
        return True

    # update or create
    @classmethod
    def update_or_create_schedule(cls, user, start, end, date, duration, avail_id, worker, task,
                                  schedule_id=None, source='auto', document=None):

        if schedule_id:
            schedule_obj = WorkerScheduled.objects.update_or_create(
                                                                     id=schedule_id,
                                                                     defaults={
                                                                         'created_by': user,
                                                                         'duration': duration,
                                                                         'time_start': start,
                                                                         'time_end': end,
                                                                         'source': source,
                                                                         'document': document,
                                                                         'name': worker,
                                                                         'date': date,
                                                                         'task_id': task,
                                                                         'available_id': avail_id
                                                                     })
        else:
            schedule_obj = WorkerScheduled.objects.update_or_create(name=worker,
                                                                         date=date,
                                                                         task_id=task,
                                                                         available_id=avail_id,
                                                                         defaults={
                                                                             'created_by': user,
                                                                             'duration': duration,
                                                                             'time_start': start,
                                                                             'time_end': end,
                                                                             'source': source,
                                                                             'document': document
                                                                         })

        cls.sync_task_by_id(task.id, 'Scheduled')
        cls.sync_avail_by_id(avail_id.id)

        return schedule_obj

    @classmethod
    def update_or_create_available(cls, user, start, end, date, duration, deduction, worker,
                                   avail_id=None, source='auto', document=None):

        if avail_id:
            avail_obj = WorkerAvailable.objects.update_or_create(id=avail_id,
                                                                 defaults={
                                                                     'created_by': user,
                                                                     'name': worker,
                                                                     'date': date,
                                                                     'duration': duration,
                                                                     'deduction': deduction,
                                                                     'time_start': start,
                                                                     'time_end': end,
                                                                     'source': source,
                                                                     'document': document
                                                                 })
        else:
            avail_obj = WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'created_by': user,
                                                                     'name': worker,
                                                                     'date': date,
                                                                     'duration': duration,
                                                                     'deduction': deduction,
                                                                     'time_start': start,
                                                                     'time_end': end,
                                                                     'source': source,
                                                                     'document': document
                                                                 })
            avail_id = avail_obj[0].id
        cls.sync_avail_by_id(avail_id)

        return avail_obj

    # high level method

    @classmethod
    def remove_schedule_by_date_range_and_worker(cls, start, end, worker):
        schedules = WorkerScheduled.objects.filter(date__range=[start, end],
                                                   name__exact=worker)
        for schedule in schedules:
            cls.remove_schedule_by_id(schedule.id)

        return True

    @classmethod
    def remove_available_by_date_range_and_worker(cls, start, end, worker):
        availables = WorkerAvailable.objects.filter(date__range=[start, end],
                                                    name__exact=worker)

        for available in availables:
            cls.remove_available_by_id(available.id)

        return True