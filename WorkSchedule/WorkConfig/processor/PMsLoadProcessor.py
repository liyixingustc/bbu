import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from ...WorkConfig.models.models import *
from ...WorkWorkers.models.models import *
from ...WorkTasks.models.models import *

from utils.UDatetime import UDatetime
from utils.UStringParser import UStringParser

EST = pytz.timezone(TIME_ZONE)


class PMsLoadProcessor:

    @classmethod
    def pms_load_processor(cls, files_path=None):

        if files_path:
            for file_path in files_path:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path)
                    cls.pms_data_processor(data)
            else:
                return JsonResponse({})
        else:
            files = Documents.objects.filter(status__exact='new', file_type__exact='PMs')
            if files.exists():
                for file in files:
                    path = BASE_DIR + file.document.url
                    if os.path.exists(path):
                        data = pd.read_excel(path)
                        cls.pms_data_processor(data)
                        # update documents
                        Documents.objects.filter(id=file.id).update(status='loaded')

                        return JsonResponse({})
            else:
                return JsonResponse({})

    @classmethod
    def pms_data_processor(cls, data):
        for index, row in data.iterrows():
            duration = timedelta(hours=row['Duration'])
            due_days = UStringParser.task_description_parser(row['Description'])['due_days']
            PMs.objects.update_or_create(masterjob_id=row['Master Job ID'],
                                         defaults={
                                             'description': row['Description'],
                                             'schedule_type': row['Schedule Type'],
                                             'duration': duration,
                                             'PMs_type': row['Type'],
                                             'due_days': due_days
                                         })
