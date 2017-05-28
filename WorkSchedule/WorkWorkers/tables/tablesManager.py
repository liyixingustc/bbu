import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse

from ..models.models import *
from ...WorkConfig.models import *


class WorkerTableManager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, period_start, period_end):

        workers = Workers.objects.all().values_list('name')
        data = pd.DataFrame()

        return data


