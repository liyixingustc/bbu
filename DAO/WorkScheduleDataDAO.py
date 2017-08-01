import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from django.db.models.functions import Concat
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkScheduleDataDAO:

    @classmethod
    def get_task_scheduled(cls, task_id):
        pass

    @classmethod
    def get_all_tasks_scheduled(cls):

        tasks = Tasks.objects.filter(current_status__in=['new', 'pending']).exclude(priority__in=['T', 'O'])\
                                                                           .values('line',
                                                                                   'work_order',
                                                                                   'description',
                                                                                   'AOR__worker__name',
                                                                                   'estimate_hour',
                                                                                   'work_type',
                                                                                   'priority',
                                                                                   'kitted_date'
                                                                                   )\
                                                            .annotate(schedule_hour=Sum('workerscheduled__duration'))
        tasks_record = pd.DataFrame.from_records(tasks)
        tasks_record.rename_axis({'AOR__worker__name': 'AOR'}, axis=1, inplace=True)

        tasks_record['schedule_hour'].fillna(timedelta(hours=0),inplace=True)
        tasks_record['balance_hour'] = tasks_record['estimate_hour'] - tasks_record['schedule_hour']

        tasks_record['schedule_hour'] = tasks_record['schedule_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['estimate_hour'] = tasks_record['estimate_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks_record['balance_hour'] = tasks_record['balance_hour'].apply(lambda x: x.total_seconds()/3600)
        now_date = UDatetime.now_local().date()
        tasks_record['OLD'] = tasks_record['kitted_date'].apply(lambda x: int((now_date - x.date()).total_seconds()/(3600*24)))
        tasks_record.drop('kitted_date',axis=1,inplace=True)

        return tasks_record

    @classmethod
    def get_all_workers_by_date_range(cls, start, end):

        # init employee
        workers = Workers.objects\
            .exclude(name__exact='NONE') \
            .filter(status__exact='active') \
            .annotate(
                available_hour=Sum(
                    models.Case(
                        models.When(workeravailable__date__range=[start,
                                                                  end],
                                    then='workeravailable__duration'),
                        default=0,
                        output_field=models.DurationField(),
                    )
                ),
                deduction=Sum(
                    models.Case(
                        models.When(workeravailable__date__range=[start,
                                                                  end],
                                    then='workeravailable__deduction'),
                        default=0,
                        output_field=models.DurationField(),
                    )
                ),
                scheduled_hour=Sum(
                    models.Case(
                        models.When(workerscheduled__date__range=[start,
                                                                  end],
                                    then='workerscheduled__duration'),
                        default=0,
                        output_field=models.DurationField(),
                    )
                ),
            )
        workers_df = pd.DataFrame.from_records(workers.values('id',
                                                              'name',
                                                              'available_hour',
                                                              'deduction',
                                                              'scheduled_hour',
                                                              'company',
                                                              'type'
                                                              )
                                               )

        workers_df = workers_df[~((workers_df['type'] == 'contractor') &
                                (workers_df['available_hour'] == timedelta()))]

        for index, row in workers_df.iterrows():
            if row['type'] == 'contractor':
                workers_df.set_value(index, 'name', row['company'])
        workers_df['id'] = workers_df['id'].astype('str')

        workers_df['balance'] = workers_df['available_hour'] - workers_df['deduction'] - workers_df['scheduled_hour']
        workers_df['balance'] = workers_df['balance'].apply(lambda x: np.round(x.total_seconds()/3600, 2))

        workers_df.sort_values('name', inplace=True)

        return workers_df
