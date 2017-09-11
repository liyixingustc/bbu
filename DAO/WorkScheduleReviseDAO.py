import numpy as np
import pandas as pd
import pytz
import re
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
    def sync_task_by_id(cls, task_id, current_status=None):
        scheduled_hour_by_task_id = WorkScheduleDataDAO.get_schedule_hour_by_task_id(task_id)
        if current_status:
            Tasks.objects.filter(id=task_id).update(current_status=current_status,
                                                    scheduled_hour=scheduled_hour_by_task_id)
        else:
            Tasks.objects.filter(id=task_id).update(scheduled_hour=scheduled_hour_by_task_id)
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
            task_priority = schedule_obj[0].task_id.priority

            available_id = schedule_obj[0].available_id.id
            schedule_obj = WorkerScheduled.objects.filter(id__exact=schedule_id)

            if task_priority in ['O', 'T']:
                cls.remove_task_by_id(task_id)

            schedule_obj.delete()
            if task_priority not in ['O', 'T']:
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

        task_priority = task.priority
        if task_priority in ['O', 'T']:
            current_status = 'Complete'
        else:
            current_status = 'Scheduled'
        cls.sync_task_by_id(task.id, current_status)
        cls.sync_avail_by_id(avail_id.id)

        return schedule_obj[0]

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

        return avail_obj[0]

    @classmethod
    def create_or_update_task(cls,
                              work_order, created_by,
                              description=None,
                              work_type=None,
                              current_status='Complete',
                              line=None,
                              shift=None,
                              priority=None,
                              create_date=None,
                              current_status_somax='Complete', schedule_date_somax=None,
                              actual_date_somax=None,
                              estimate_hour=timedelta(hours=0),
                              scheduled_hour=timedelta(hours=0),
                              actual_hour=timedelta(hours=0),
                              fail_code=None, completion_comments=None,
                              equipment=None, aor=None, creator=None, assigned=None, pms=None,
                              created_on=None,
                              task_id=None, source='auto', document=None):

        if not create_date:
            create_date = UDatetime.now_local()
        if not created_on:
            created_on = UDatetime.now_local()

        if task_id:
            task_obj = Tasks.objects.update_or_create(
                id=task_id,
                defaults={
                    'work_order': work_order,
                    'description': description,
                    'work_type': work_type,
                    'current_status': current_status,
                    'line': line,
                    'shift': shift,
                    'priority': priority,
                    'create_date': create_date,
                    'current_status_somax': current_status_somax,
                    'schedule_date_somax': schedule_date_somax,
                    'actual_date_somax': actual_date_somax,
                    'estimate_hour': estimate_hour,
                    'scheduled_hour': scheduled_hour,
                    'actual_hour': actual_hour,
                    'fail_code': fail_code,
                    'completion_comments': completion_comments,
                    'equipment': equipment,
                    'AOR': aor,
                    'creator': creator,
                    'assigned': assigned,
                    'PMs': pms,
                    'created_by': created_by,
                    'created_on': created_on,
                    'source': source,
                    'document': document
                })
        else:
            task_obj = Tasks.objects.update_or_create(
                work_order=work_order,
                defaults={
                    'description': description,
                    'work_type': work_type,
                    'current_status': current_status,
                    'line': line,
                    'shift': shift,
                    'priority': priority,
                    'create_date': create_date,
                    'current_status_somax': current_status_somax,
                    'schedule_date_somax': schedule_date_somax,
                    'actual_date_somax': actual_date_somax,
                    'estimate_hour': estimate_hour,
                    'scheduled_hour': scheduled_hour,
                    'actual_hour': actual_hour,
                    'fail_code': fail_code,
                    'completion_comments': completion_comments,
                    'equipment': equipment,
                    'AOR': aor,
                    'creator': creator,
                    'assigned': assigned,
                    'PMs': pms,
                    'created_by': created_by,
                    'created_on': created_on,
                    'source': source,
                    'document': document
                })
            task_id = task_obj[0].id
        cls.sync_task_by_id(task_id)

        return task_obj[0]

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

    # other special tasks
    @classmethod
    def create_or_update_union_bus_task(cls, created_by, estimate_hour,
                                        work_order=None,
                                        current_status='Complete',
                                        current_status_somax='Complete',
                                        task_id=None,
                                        source='auto', document=None):

        if not work_order:
            work_order = cls.get_latest_available_work_order('O')
        task_obj = cls.create_or_update_task(work_order=work_order, created_by=created_by,
                                             description='Union Business',
                                             priority='O',
                                             current_status=current_status,
                                             current_status_somax=current_status_somax,
                                             estimate_hour=estimate_hour,
                                             task_id=task_id,
                                             source=source, document=document)

        return task_obj

    @classmethod
    def create_or_update_timeoff_lunch_task(cls, created_by,
                                            work_order=None,
                                            current_status='Complete',
                                            current_status_somax='Complete',
                                            task_id=None,
                                            source='auto', document=None):

        if not work_order:
            work_order = cls.get_latest_available_work_order('T')
        task_obj = cls.create_or_update_task(work_order=work_order, created_by=created_by,
                                             description='Lunch Time',
                                             priority='T',
                                             current_status=current_status,
                                             current_status_somax=current_status_somax,
                                             estimate_hour=timedelta(minutes=30),
                                             task_id=task_id,
                                             source=source, document=document)

        return task_obj

    @classmethod
    def create_or_update_timeoff_breaks_task(cls, created_by,
                                             work_order=None,
                                             current_status='Complete',
                                             current_status_somax='Complete',
                                             task_id=None,
                                             source='auto', document=None):

        if not work_order:
            work_order = cls.get_latest_available_work_order('T')
        task_obj = cls.create_or_update_task(work_order=work_order, created_by=created_by,
                                             description='Break Time',
                                             priority='T',
                                             current_status=current_status,
                                             current_status_somax=current_status_somax,
                                             estimate_hour=timedelta(minutes=15),
                                             task_id=task_id,
                                             source=source, document=document)

        return task_obj

    @classmethod
    def get_latest_available_work_order(cls, work_type=None):
        work_order = None
        regex = re.compile(r'(?P<work_type>\w)?(?P<order_number>\d*)?')
        if work_type == 'T':
            tasks_obj = Tasks.objects.filter(priority__exact='T')
            if tasks_obj.exists():
                tasks_df = pd.DataFrame.from_records(tasks_obj.values('work_order'))
                tasks_df = tasks_df['work_order'].str.extract(regex, expand=True)
                tasks_df['order_number'] = tasks_df['order_number'].astype(int)
                tasks_df.sort_values('order_number', inplace=True)
                order_number = tasks_df.iloc[-1]['order_number']
                if order_number:
                    work_order = 'T' + str((order_number+1))
                else:
                    work_order = None
            else:
                work_order = 'T1'
        elif work_type == 'O':
            tasks_obj = Tasks.objects.filter(priority__exact='O')
            if tasks_obj.exists():
                tasks_df = pd.DataFrame.from_records(tasks_obj.values('work_order'))
                tasks_df = tasks_df['work_order'].str.extract(regex, expand=True)
                tasks_df['order_number'] = tasks_df['order_number'].astype(int)
                tasks_df.sort_values('order_number', inplace=True)
                order_number = tasks_df.iloc[-1]['order_number']
                if order_number:
                    work_order = 'O' + str((order_number+1))
                else:
                    work_order = None
            else:
                work_order = 'O1'
        else:
            pass

        return work_order
