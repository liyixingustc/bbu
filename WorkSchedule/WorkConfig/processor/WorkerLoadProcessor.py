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

EST = pytz.timezone(TIME_ZONE)


class WorkerLoadProcessor:

    @classmethod
    def worker_load_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='Worker')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_excel(path)
                    for index, row in data.iterrows():
                        company = Company.objects.get(business_name__exact=row['company'])
                        somax_account = SomaxAccount.objects.filter(full_name__exact=row['name'])
                        if somax_account:
                            somax_account = somax_account[0]
                        else:
                            somax_account = None
                        Workers.objects.update_or_create(id=row['id'],
                                                         defaults={
                                                             'name': row['name'],
                                                             'last_name': row['last_name'],
                                                             'first_name': row['first_name'],
                                                             'company': company,
                                                             'level': row['level'],
                                                             'shift': row['shift'],
                                                             'type': row['type'],
                                                             'somax_account': somax_account
                                                         })
                    # update documents
                    # Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})
