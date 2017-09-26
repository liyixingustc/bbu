from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
import pandas as pd
import re
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from bbu.settings import TIME_ZONE

from django.db import models
from ...WorkWorkers.models.models import *
from ...WorkTasks.models.models import *

from DAO.WorkScheduleReviseDAO import WorkScheduleReviseDAO

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class SmartScheduler:

    def __init__(self, request, start, end):
        self.request = request
        self.start = start
        self.end = end

        # self.start = dt(2017, 8, 27, 0, 0, 0, tzinfo=EST)
        # self.end = dt(2017, 8, 30, 0, 0, 0, tzinfo=EST)

        self.data_init()

    def data_init(self):
        open_tasks = ['Approved']
        data = Tasks.objects.filter(current_status__in=open_tasks,
                                    create_date__range=[self.start, self.end],
                                    )\
                            .exclude(estimate_hour__exact=timedelta(hours=0))
        self.data = pd.DataFrame.from_records(data.values())

    def scheduler_scheduled_tasks(self):

        if self.data.empty:
            return

        data = self.data[
                         (~self.data['schedule_date_somax'].isnull()) &
                         (self.data['schedule_date_somax'] >= dt(2000, 1, 1)) &
                         (~self.data['assigned_id'].isnull())
                        ]

        if data.empty:
            return

        data = data[790:800]

        for index, row in data.iterrows():
            work_order = row['work_order']
            scheduled_date = row['schedule_date_somax'].date()
            estimate_hour = row['estimate_hour']
            assigned_id = row['assigned_id']

            task = Tasks.objects.filter(work_order__exact=work_order)

            if not task.exists():
                continue
            else:
                task = task[0]

            worker = Workers.objects.filter(somax_account__id__exact=assigned_id)
            if not worker.exists():
                continue
            else:
                worker = worker[0]

            availables = WorkerAvailable.objects.filter(name=worker, date__gte=scheduled_date)\
                                                .order_by('date', 'time_start')[:10]
            if availables.exists():

                # add schedule
                is_scheduled = False
                for available in availables:
                    if is_scheduled:
                        break
                    available_df = self.scheduled_substract(available)
                    if not available_df.empty:
                        for avail_index, avail_row in available_df.iterrows():
                            available_id = avail_row['id']
                            available_start = avail_row['time_start']
                            available_end = avail_row['time_end']

                            # check downday
                            is_downday = self.is_downday(available_start, available_end)

                            # if available_start.weekday() == 6:
                            #     print(is_downday, available_start.weekday(), UDatetime.to_local(available_start),UDatetime.to_local(available_end),worker.name)

                            if is_downday:
                                is_scheduled = False
                                break

                            # add schedule
                            result = self.add_schedule(self.request, available_start, available_end, scheduled_date,
                                                       estimate_hour,
                                                       available_id, worker, task)
                            if result:
                                is_scheduled = True
                                break

    @classmethod
    def add_schedule(cls, request, start, end, date, est, avail_id, worker, task):
        available_duration = end - start
        if available_duration >= est:
            available_id = WorkerAvailable.objects.get(id=avail_id)
            # WorkScheduleReviseDAO.update_or_create_schedule(request.user, start, start + est, date, est,
            #                                                 available_id, worker, task)
            return True
        else:
            return False

    @classmethod
    def scheduled_substract(cls, available):
        available_df = pd.DataFrame(available.__dict__, index=[0])
        scheduled = WorkerScheduled.objects.filter(available_id=available)

        # update available by scheduled tasks
        if scheduled.exists():
            scheduled_df = pd.DataFrame.from_records(scheduled.values())
            for index_scheduled, row_scheduled in scheduled_df.iterrows():
                scheduled_start = row_scheduled['time_start']
                scheduled_end = row_scheduled['time_end']

                for index_avail, row_avail in available_df.iterrows():
                    available_start = row_avail['time_start']
                    available_end = row_avail['time_end']

                    available_new = UDatetime.remove_overlap(available_start,
                                                             available_end,
                                                             scheduled_start,
                                                             scheduled_end)

                    available_start = available_new[0][0].astimezone('UTC')
                    available_end = available_new[0][1].astimezone('UTC')

                    available_df.set_value(index_avail, 'time_start', available_start)
                    available_df.set_value(index_avail, 'time_end', available_end)

                    if len(available_new) == 2:
                        available_start_addition = available_new[1][0]
                        available_end_addition = available_new[1][1]
                        available_addition_row = available_df.iloc[index_avail]
                        available_addition_row.set_value('time_start', available_start_addition.astimezone('UTC'))
                        available_addition_row.set_value('time_end', available_end_addition.astimezone('UTC'))
                        available_df = available_df.append(available_addition_row, ignore_index=True)
        available_df.sort_values(['date', 'time_start'], inplace=True)

        return available_df

    @classmethod
    def is_downday(cls, start, end):

        from configuration.WorkScheduleConstants import PMs

        bread_downday_start = cls.downday_str_parser(PMs.Bread.Downdays.start, start.year, start.isocalendar()[1])
        bread_downday_end = cls.downday_str_parser(PMs.Bread.Downdays.end, start.year, start.isocalendar()[1]+1)
        em_downday_start = cls.downday_str_parser(PMs.EM.Downdays.start, start.year, start.isocalendar()[1])
        em_downday_end = cls.downday_str_parser(PMs.EM.Downdays.end, start.year, start.isocalendar()[1])

        overlap = UDatetime.get_overlap(start, end, bread_downday_start, bread_downday_end)
        if overlap.total_seconds() == 0:
            return False
        else:
            return True

    @staticmethod
    def downday_str_parser(string, year, week_number):

        regex = re.compile(
            r'(?P<weekday>[a-zA-Z]+)\s*(?P<hour>[0-9]+):(?P<min>[0-9]+)'
        )

        parts = regex.match(string)

        if parts:
            parts = parts.groupdict()
        else:
            return None

        str_new = '{year}-{week_number}-{weekday}-{hour}-{min}' \
            .format(year=year,
                    week_number=week_number,
                    weekday=parts['weekday'],
                    hour=parts['hour'],
                    min=parts['min']
                    )

        downday = UDatetime.localize(dt.strptime(str_new, '%Y-%W-%a-%H-%M'))
        return downday

    def run(self):

        self.scheduler_scheduled_tasks()