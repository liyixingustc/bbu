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


class PMsLoadProcessor:

    @classmethod
    def pms_load_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='PMs')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_excel(path)

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})