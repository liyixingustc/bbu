import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

# from ..models.models import *
from ...WorkConfig.models import *
from ...WorkWorkers.models.models import *


class WorkSchedulerPanel2Table1Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls):

        tasks = Tasks.objects.filter(current_status__in=['new', 'pending']).values('line',
                                                                                     'work_order',
                                                                                     'schedule_hour',
                                                                                     'estimate_hour',
                                                                                     'work_type',
                                                                                     'priority',
                                                                                     'create_on',
                                                                                     'actual_hour')

        tasks = pd.DataFrame.from_records(tasks, columns=['line',
                                                          'work_order',
                                                          'schedule_hour',
                                                          'estimate_hour',
                                                          'work_type',
                                                          'priority',
                                                          'create_on',
                                                          'actual_hour'])

        tasks['schedule_hour'] = tasks['schedule_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks['estimate_hour'] = tasks['estimate_hour'].apply(lambda x: x.total_seconds()/3600)
        tasks['actual_hour'] = tasks['actual_hour'].apply(lambda x: x.total_seconds()/3600)

        data = tasks

        return data
