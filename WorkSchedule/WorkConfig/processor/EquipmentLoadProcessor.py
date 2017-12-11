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


class EquipmentLoadProcessor:

    @classmethod
    def equipment_load_processor(cls, files_path=None):

        if files_path:
            for file_path in files_path:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path)
                    cls.equipment_data_processor(data)
            else:
                return JsonResponse({})
        else:
            files = Documents.objects.filter(status__exact='new', file_type__exact='Equipment')
            if files.exists():
                for file in files:
                    path = BASE_DIR + file.document.url
                    if os.path.exists(path):
                        data = pd.read_csv(path)
                        cls.equipment_data_processor(data)
                        # update documents
                        Documents.objects.filter(id=file.id).update(status='loaded')
                        return JsonResponse({})
            else:
                return JsonResponse({})

    @classmethod
    def equipment_data_processor(cls, data):

        for index, row in data.iterrows():
            equipment_name_clean = ''.join(row['Name'].split()).upper()
            Equipment.objects.update_or_create(equipment_id=row['Equipment ID'],
                                               defaults={
                                                   'equipment_name': row['Name'],
                                                   'location': row['Location'],
                                                   'serial_no': row['Serial No'],
                                                   'equipment_type': row['Type'],
                                                   'make': row['Make'],
                                                   'model_no': row['Model No'],
                                                   'account': row['Account'],
                                                   'asset_number': row['Asset Number'],
                                                   'area': row['Area'],
                                                   'department': row['Department'],
                                                   'line': row['Line'],
                                                   'equipment_name_clean': equipment_name_clean
                                               })