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


class PartsOpenProcessor:

    @classmethod
    def parts_open_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='PartsOpen')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_excel(path)
                    data['AWAITING'] = data['AWAITING'].str.upper()
                    data = data[data['AWAITING'] == 'Y']

                    not_received_list_raw = list(data['WORK ORDER'].unique())
                    not_received_list = []
                    pattern = re.compile('^[0-9]{5,20}$')
                    for order in not_received_list_raw:
                        if re.match(pattern, str(order)):
                            not_received_list += [str(order)]
                        else:
                            order_splitted = order.split()
                            for i in order_splitted:
                                if re.match(pattern, str(i)):
                                    not_received_list += [str(i)]
                    not_received_list = list(set(not_received_list))

                    Tasks.objects.filter(current_status__exact='Wait For Parts').update(current_status='Approved')
                    Tasks.objects.filter(work_order__in=not_received_list).update(current_status='Wait For Parts')

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})
