import numpy as np
import pandas as pd
import pytz
import ast

from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from django.db.models.functions import Concat
from django.core.paginator import Paginator
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkScheduleDataDAO:

    open_tasks_status = ['Approved', 'Scheduled', 'Work Request']
    ready_for_schedule_tasks_status = ['Approved', 'Scheduled']

    @classmethod
    def get_all_tasks_open_num(cls):
        num = Tasks.objects.filter(current_status__in=cls.ready_for_schedule_tasks_status) \
            .exclude(priority__in=['T', 'O']).count()

        return num

    @classmethod
    def get_all_schedules_sync_to_somax(cls):

        tasks = Tasks.objects.filter(current_status__in=cls.ready_for_schedule_tasks_status,
                                     sync_to_somax__in=['no', 'error'])\
            .exclude(priority__in=['T', 'O'])

        tasks_record = pd.DataFrame.from_records(tasks
                                                 .values('line',
                                                         'work_order',
                                                         'description',
                                                         'AOR__worker__name',
                                                         'estimate_hour',
                                                         'work_type',
                                                         'priority',
                                                         'create_date',
                                                         'current_status',
                                                         'workerscheduled__date',
                                                         'workerscheduled__name__somax_account',
                                                         'sync_to_somax'
                                                         )
                                                 .annotate(schedule_hour=Sum('workerscheduled__duration'))
                                                 )

        tasks_record.rename_axis({'AOR__worker__name': 'AOR'}, axis=1, inplace=True)
        tasks_record.rename_axis({'workerscheduled__date': 'date'}, axis=1, inplace=True)
        tasks_record.rename_axis({'workerscheduled__name__somax_account': 'worker'}, axis=1, inplace=True)

        if tasks_record.empty:
            return pd.DataFrame()

        tasks_record['schedule_hour'].fillna(timedelta(hours=0), inplace=True)
        tasks_record['schedule_hour'] = tasks_record['schedule_hour'].apply(lambda x: x.total_seconds() / 3600)

        now_date = UDatetime.now_local().date()
        tasks_record['OLD'] = tasks_record['create_date'].apply(
            lambda x: int((now_date - x.date()).total_seconds() / (3600 * 24)))
        tasks_record.drop('create_date', axis=1, inplace=True)

        return tasks_record

    @classmethod
    def get_all_tasks_open(cls, pagination=False, page_size=None, offset=None, filters=None, sort=None, order=None):

        if sort and order:
            if sort == 'OLD':
                sort = 'create_date'
            elif sort == 'balance_hour':
                sort = 'estimate_hour'
            if order == 'desc':
                sort = '-'+sort
        else:
            sort = 'work_order'

        tasks = Tasks.objects.filter(current_status__in=cls.ready_for_schedule_tasks_status)\
            .exclude(priority__in=['T', 'O']) \
            .annotate(schedule_hour=Sum('workerscheduled__duration')) \
            .order_by(sort)

        if filters:
            filters = ast.literal_eval(filters)
            if filters.get('work_order'):
                tasks = tasks.filter(work_order__contains=filters['work_order'])
            if filters.get('description'):
                tasks = tasks.filter(description__contains=filters['description'])
            if filters.get('estimate_hour'):
                try:
                    est = float(filters['estimate_hour'])
                    tasks = tasks.filter(estimate_hour__exact=timedelta(hours=est))
                except Exception as e:
                    pass
            if filters.get('AOR'):
                tasks = tasks.filter(AOR__worker__name__contains=filters['AOR'])
            if filters.get('work_type'):
                tasks = tasks.filter(work_type__exact=filters['work_type'])
            if filters.get('priority'):
                tasks = tasks.filter(priority__exact=filters['priority'])
            if filters.get('current_status'):
                tasks = tasks.filter(current_status__exact=filters['current_status'])
            if filters.get('sync_to_somax'):
                tasks = tasks.filter(sync_to_somax__exact=filters['sync_to_somax'])

        num = tasks.count()

        if pagination:
            paginator = Paginator(tasks, page_size,)
            current_page = int(offset/page_size) + 1
            tasks = paginator.page(current_page).object_list

        tasks_record = pd.DataFrame.from_records(tasks
                                                 .values('line',
                                                         'work_order',
                                                         'description',
                                                         'AOR__worker__name',
                                                         'estimate_hour',
                                                         'work_type',
                                                         'priority',
                                                         'create_date',
                                                         'current_status',
                                                         'schedule_hour',
                                                         'sync_to_somax'
                                                         ))
        tasks_record.rename_axis({'AOR__worker__name': 'AOR'}, axis=1, inplace=True)

        if tasks_record.empty:
            return pd.DataFrame(), 0

        tasks_record['schedule_hour'].fillna(timedelta(hours=0), inplace=True)
        tasks_record['balance_hour'] = tasks_record['estimate_hour'] - tasks_record['schedule_hour']

        tasks_record['schedule_hour'] = tasks_record['schedule_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['estimate_hour'] = tasks_record['estimate_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['balance_hour'] = tasks_record['balance_hour'].apply(lambda x: x.total_seconds()/3600)
        now_date = UDatetime.now_local().date()
        tasks_record['OLD'] = tasks_record['create_date'].apply(lambda x: int((now_date - x.date()).total_seconds()/(3600*24)))
        tasks_record.drop('create_date', axis=1, inplace=True)

        return tasks_record, num

    @classmethod
    def get_all_tasks_scheduled(cls):

        tasks = Tasks.objects.filter(current_status__exact='Scheduled')\
            .exclude(priority__in=['T', 'O'])\
            .values('line',
                    'work_order',
                    'description',
                    'AOR__worker__name',
                    'estimate_hour',
                    'work_type',
                    'priority',
                    'create_date',
                    'current_status'
                    )\
            .annotate(schedule_hour=Sum('workerscheduled__duration'))
        tasks_record = pd.DataFrame.from_records(tasks)
        tasks_record.rename_axis({'AOR__worker__name': 'AOR'}, axis=1, inplace=True)

        if tasks_record.empty:
            return pd.DataFrame()

        tasks_record['schedule_hour'].fillna(timedelta(hours=0),inplace=True)
        tasks_record['balance_hour'] = tasks_record['estimate_hour'] - tasks_record['schedule_hour']

        tasks_record['schedule_hour'] = tasks_record['schedule_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['estimate_hour'] = tasks_record['estimate_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['balance_hour'] = tasks_record['balance_hour'].apply(lambda x: x.total_seconds()/3600)
        now_date = UDatetime.now_local().date()
        tasks_record['OLD'] = tasks_record['create_date'].apply(lambda x: int((now_date - x.date()).total_seconds()/(3600*24)))
        tasks_record.drop('create_date', axis=1, inplace=True)

        return tasks_record

    @classmethod
    def get_all_workers_by_date_range(cls, start, end):

        # query pipline
        workers_available_hour = Workers.objects \
            .exclude(name__exact='NONE') \
            .filter(status__exact='active') \
            .annotate(
            available_hour=Sum(
                models.Case(
                    models.When(workeravailable__date__range=[start, end],
                                then='workeravailable__duration'),
                    default=0,
                    output_field=models.DurationField(),
                )
            ),
        )

        workers_deduction = Workers.objects \
            .exclude(name__exact='NONE') \
            .filter(status__exact='active') \
            .annotate(
            available_hour=Sum(
                models.Case(
                    models.When(workeravailable__date__range=[start, end],
                                then='workeravailable__duration'),
                    default=0,
                    output_field=models.DurationField(),
                )
            ),
            deduction=Sum(
                models.Case(
                    models.When(workeravailable__date__range=[start, end],
                                then='workeravailable__deduction'),
                    default=0,
                    output_field=models.DurationField(),
                )
            ),
        )

        workers_scheduled_hour = Workers.objects \
            .exclude(name__exact='NONE') \
            .filter(status__exact='active') \
            .annotate(
            scheduled_hour=Sum(
                models.Case(
                    models.When(workerscheduled__date__range=[start, end],
                                then='workerscheduled__duration'),
                    default=0,
                    output_field=models.DurationField(),
                )
            ),
        )

        # to df
        workers_available_hour_df = pd.DataFrame.from_records(workers_available_hour.values('id',
                                                                                            'name',
                                                                                            'available_hour',
                                                                                            'company',
                                                                                            'shift',
                                                                                            'status',
                                                                                            'type'
                                                                                            ))
        workers_deduction_df = pd.DataFrame.from_records(workers_deduction.values('id',
                                                                                  'deduction',
                                                                                  ))
        workers_scheduled_hour_df = pd.DataFrame.from_records(workers_scheduled_hour.values('id',
                                                                                            'scheduled_hour',
                                                                                            ))

        # join df
        workers_df = pd.merge(
            pd.merge(workers_available_hour_df, workers_deduction_df, on='id'),
            workers_scheduled_hour_df,
            on='id')

        return workers_df

    @classmethod
    def get_all_include_workers_by_date_range(cls, start, end):

        workers_df = cls.get_all_workers_by_date_range(start, end)

        # process data
        workers_df = workers_df[~(
            ((workers_df['type'] == 'contractor') & (workers_df['available_hour'] == timedelta())) |
            (workers_df['status'] == 'inactive')
        )]

        workers_df['id'] = workers_df['id'].astype('str')

        workers_df['balance'] = workers_df['available_hour'] - workers_df['scheduled_hour']
        workers_df['balance'] = workers_df['balance'].apply(lambda x: np.round(x.total_seconds()/3600, 2))

        workers_df.sort_values('name', inplace=True)

        return workers_df

    @classmethod
    def get_all_exclude_workers_by_date_range(cls, start, end):

        workers_df = cls.get_all_workers_by_date_range(start, end)

        # process data
        workers_df = workers_df[(
            ((workers_df['type'] == 'contractor') & (workers_df['available_hour'] == timedelta())) |
            (workers_df['status'] == 'inactive')
        )]

        workers_df['id'] = workers_df['id'].astype('str')

        workers_df['balance'] = workers_df['available_hour'] - workers_df['deduction'] - workers_df['scheduled_hour']
        workers_df['balance'] = workers_df['balance'].apply(lambda x: np.round(x.total_seconds()/3600, 2))

        workers_df.sort_values('name', inplace=True)

        return workers_df

    @classmethod
    def get_schedule_hour_by_task_id(cls, task_id):
        schedule_hour_obj = Tasks.objects.filter(id=task_id).annotate(schedule_hour=Sum('workerscheduled__duration'))
        schedule_hour = schedule_hour_obj[0].schedule_hour
        if not schedule_hour:
            schedule_hour = timedelta(hours=0)
        return schedule_hour

    @classmethod
    def get_schedule_hour_by_available_id(cls, available_id):
        schedule_hour_obj = WorkerAvailable.objects.filter(id=available_id).annotate(schedule_hour=Sum('workerscheduled__duration'))
        schedule_hour = schedule_hour_obj[0].schedule_hour
        if not schedule_hour:
            schedule_hour = timedelta(hours=0)
        return schedule_hour
