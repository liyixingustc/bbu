from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from bbu.settings import TIME_ZONE

from django.db import models
from ...WorkWorkers.models.models import *
from ...WorkTasks.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class SmartScheduler:

    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.start = dt(2017, 8, 27, 0, 0, 0, tzinfo=EST)
        self.end = dt(2017, 8, 30, 0, 0, 0, tzinfo=EST)

        self.data_init()

    def data_init(self):
        open_tasks = ['Approved', 'Scheduled', 'Work Request']
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
        i=0
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

            available = WorkerAvailable.objects.filter(name=worker, date=scheduled_date)
            if not available.exists():
                continue

            scheduled = WorkerScheduled.objects.filter(name=worker, date=scheduled_date)

            i+=1
        print(i)

    def run(self):

        self.scheduler_scheduled_tasks()