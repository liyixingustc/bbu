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


class AORLoadProcessor:
    @classmethod
    def aor_load_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='AOR')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_excel(path)

                    for index, row in data.iterrows():

                        worker = Workers.objects.get(name__exact=row['worker'].upper())

                        equip_id = cls.filter_equipment_by_equipment_name(row['equip name'])
                        if not equip_id:
                            equip_id = cls.filter_equipment_by_clean_equipment_name(row['equip name'])

                        AOR.objects.update_or_create(id=row['id'],
                                                     defaults={
                                                         'worker': worker,
                                                         'line': row['line'],
                                                         'AOR_type': row['type'],
                                                         'equip_name': row['equip name'],
                                                         'equip_code': row['equip code'],
                                                         'equip_id': equip_id
                                                     })

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})

    @classmethod
    def filter_equipment_by_equipment_code(cls):
        pass

    @classmethod
    def filter_equipment_by_clean_equipment_name(cls, equip_name):

        equipment_name_clean = ''.join(equip_name.split()).upper()
        equip_id = Equipment.objects.filter(equipment_name_clean__exact=equipment_name_clean)
        if equip_id.exists():
            equip_id = equip_id[0]
        else:
            equip_id = None

        return equip_id

    @classmethod
    def filter_equipment_by_equipment_name(cls, equip_name):

        equip_id = Equipment.objects.filter(equipment_name__exact=equip_name)

        if equip_id.exists():
            equip_id = equip_id[0]
        else:
            equip_id = None

        return equip_id
