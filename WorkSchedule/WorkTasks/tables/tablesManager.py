import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

from ..models.models import *
from ...WorkConfig.models import *
from ...WorkWorkers.models.models import *


class WorkTasksPanel1Table1Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, period_start, period_end):

        period_start = dt.strptime(period_start, '%Y-%m-%d')
        period_end = dt.strptime(period_end, '%Y-%m-%d')
        period = pd.date_range(period_start, period_end)

        tasks = Tasks.objects.filter(period_start__exact=period_start,
                                     period_end__exact=period_end).values('line',
                                                                          'working_order',
                                                                          'schedule_hour',
                                                                          'estimate_hour',
                                                                          'description',
                                                                          'working_type',
                                                                          'priority',
                                                                          'days_old',
                                                                          'actual_hour')

        tasks = pd.DataFrame.from_records(tasks, columns=['line',
                                                          'working_order',
                                                          'schedule_hour',
                                                          'estimate_hour',
                                                          'description',
                                                          'working_type',
                                                          'priority',
                                                          'days_old',
                                                          'actual_hour'])

        tasks['schedule_hour'] = tasks['schedule_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks['estimate_hour'] = tasks['estimate_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks['actual_hour'] = tasks['actual_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks['days_old'] = tasks['days_old'].apply(lambda x: x.total_seconds()/(3600*24))

        data = tasks

        return data


class WorkTasksPanel1Table2aManager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, parameters):

        period_start = dt.strptime(parameters['period_start'], '%Y-%m-%d')
        period_end = dt.strptime(parameters['period_end'], '%Y-%m-%d')

        workerscheduled = WorkerScheduledTask.objects.filter(task_id__period_start__exact=period_start,
                                                             task_id__period_end__exact=period_end,
                                                             task_id__working_order__exact=parameters['working_order'])\
                                                                .values('workerscheduled_id__name',
                                                                        'workerscheduled_id__date',
                                                                        'workerscheduled_id__duration'
                                                                        )

        workerscheduled = pd.DataFrame.from_records(workerscheduled, columns=['workerscheduled_id__name',
                                                                              'workerscheduled_id__date',
                                                                              'workerscheduled_id__duration'
                                                                              ])

        workerscheduled.rename_axis({'workerscheduled_id__name': 'name',
                                     'workerscheduled_id__date': 'date',
                                     'workerscheduled_id__duration': 'scheduled'}, axis=1, inplace=True)

        workerscheduled['date'] = workerscheduled['date'].apply(lambda x: str(x))
        workerscheduled['scheduled'] = workerscheduled['scheduled'].apply(lambda x: x.total_seconds()/3600)

        data = workerscheduled

        return data


class WorkTasksPanel1Table2bManager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, parameters):

        period_start = dt.strptime(parameters['period_start'], '%Y-%m-%d')
        period_end = dt.strptime(parameters['period_end'], '%Y-%m-%d')

        workers_available = WorkerAvailable.objects.filter(date__range=[period_start, period_end]).values('name__name',
                                                                                                          'date',
                                                                                                          'duration')
        print(workers_available)
        workers_available = pd.DataFrame.from_records(workers_available, columns=['name__name',
                                                                                  'date',
                                                                                  'duration'
                                                                                  ])

        workers_available.rename_axis({'name__name': 'name',
                                       'duration': 'available'}, axis=1, inplace=True)
        workers_available['date'] = workers_available['date'].apply(lambda x: str(x))
        workers_available['available'] = workers_available['available'].apply(lambda x: x.total_seconds()/3600)

        data = workers_available

        return data
