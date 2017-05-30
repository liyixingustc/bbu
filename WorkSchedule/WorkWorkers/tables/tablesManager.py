import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

from ..models.models import *
from ...WorkConfig.models import *


class WorkWorkersPanel1Table1Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, period_start, period_end):

        period_start = dt.strptime(period_start,'%Y-%m-%d')
        period_end = dt.strptime(period_end,'%Y-%m-%d')
        period = pd.date_range(period_start,period_end)

        workers = Workers.objects.all().values_list('name')
        workers_available = WorkerAvailable.objects.filter(date__range=[period_start, period_end]).values('name',
                                                                                                          'date',
                                                                                                          'duration')

        workers_available = pd.DataFrame.from_records(workers_available, columns=['name', 'date', 'duration'])

        for worker in workers:
            worker = worker[0]
            for date in period:
                date = date.date()
                if not ((workers_available['name'] == worker) & (workers_available['date'] == date)).any():
                    row = pd.DataFrame([{'name': worker, 'date': date, 'duration': timedelta(hours=0)}])
                    workers_available = pd.concat([workers_available, row], ignore_index=True)

        workers_available = cls.df_week_view(workers_available)

        workers_available.rename_axis({'name': 'name',
                                       'duration': 'available'}, axis=1, inplace=True)

        data = workers_available

        return data

    @classmethod
    def df_week_view(cls, data, name='name', date='date', duration='duration'):

        data[date] = (data[date].apply(lambda x: '{date}<br/>{week}'.format(date=str(x),week=x.strftime('%a'))))
        data[duration] = data[duration].apply(lambda x: x.total_seconds()/3600)
        data = pd.pivot_table(data,values=duration,index=name,columns=date).reset_index()
        data.rename_axis(None,inplace=True)

        return data


class WorkWorkersPanel1Table2Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, parameters):

        period_start = dt.strptime(parameters['period_start'], '%Y-%m-%d')
        period_end = dt.strptime(parameters['period_end'], '%Y-%m-%d')

        tasks = WorkerScheduledTask.objects.filter(task_id__period_start__exact=period_start,
                                                   task_id__period_end__exact=period_end,
                                                   workerscheduled_id__name__name__exact=parameters['name'],
                                                   workerscheduled_id__date__range=[period_start, period_end])\
            .values('task_id__line',
                    'task_id__working_order',
                    'task_id__description',
                    'task_id__working_type',
                    'task_id__priority',
                    'workerscheduled_id__date',
                    'workerscheduled_id__duration')

        tasks = pd.DataFrame.from_records(tasks, columns=['task_id__line',
                                                          'task_id__working_order',
                                                          'task_id__description',
                                                          'task_id__working_type',
                                                          'task_id__priority',
                                                          'workerscheduled_id__date',
                                                          'workerscheduled_id__duration'])

        tasks.rename_axis({'task_id__line': 'line',
                           'task_id__working_order': 'order',
                           'task_id__description': 'description',
                           'task_id__working_type': 'type',
                           'task_id__priority': 'priority',
                           'workerscheduled_id__date': 'date',
                           'workerscheduled_id__duration': 'scheduled',
                           },
                          axis=1, inplace=True)

        tasks['scheduled'] = tasks['scheduled'].apply(lambda x: x.total_seconds()/3600)
        tasks['date'] = tasks['date'].apply(lambda x: str(x))

        data = tasks

        return data
