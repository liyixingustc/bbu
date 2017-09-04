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


class SmartScheduler:

    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.start = dt(2017, 8, 1)
        self.end = dt(2017, 9, 1)

        self.data_init()

    def data_init(self):
        open_tasks = ['Approved', 'Scheduled', 'Work Request']
        data = Tasks.objects.filter(current_status=open_tasks,
                                    create_date__range=[self.start, self.end],
                                    )\
                            .exclude(estimate_hour__exact=0)
        self.data = pd.DataFrame.from_records(data.values())

    def run(self):

        print(self.data)