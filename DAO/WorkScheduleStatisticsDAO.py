import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q
from bbu.settings import TIME_ZONE

from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkScheduleStatisticsDAO:

    @classmethod
    def avail_dao(cls, start, end, worker_names=None, date_model='round'):

        avail = timedelta(hours=0)
        avail_deduct = timedelta(hours=0)
        
        if date_model == 'round':
            start_date = UDatetime.pick_date_by_one_date(start)
            end_date = UDatetime.pick_date_by_one_date(end)
        elif date_model == 'accurate':
            start_date = start
            end_date = end
        else:
            start_date = start
            end_date = end
        
        if worker_names:
            worker = Workers.objects.filter(id__in=worker_names)
            worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date], name__in=worker_names)
        else:
            worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])

        if worker_avail.exists():
            pass

    @classmethod
    def avail_effect_dao(cls, start, end, worker_names=None, date_model='round'):
        pass

    @classmethod
    def scheduled_dao(cls, start, end, worker_names=None, date_model='round'):
        pass

    @classmethod
    def scheduled_effect_dao(cls, start, end, worker_names=None, date_model='round'):
        pass
    
    @classmethod
    def balance_dao(cls, start, end, worker_names=None, date_model='round'):
        if date_model == 'round':
            start_date = UDatetime.pick_date_by_one_date(start)
            end_date = UDatetime.pick_date_by_one_date(end)
        elif date_model == 'accurate':
            start_date = start
            end_date = end
        else:
            start_date = start
            end_date = end

        if worker_names:
            worker = Workers.objects.filter(id__in=worker_names)
            worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date], name__in=worker_names)
        else:
            worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
    
    @classmethod
    def tasks_dao(cls, start, end, worker=None, date_model='round'):
        pass