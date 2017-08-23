import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from Reports.ReportConfig.models.models import *
from Reports.ReportTimeDetail.models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class ReportLostTimeDetailProcessor:

    @classmethod
    def report_lost_time_detail_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='ReportLostTimeDetail')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    csv_data = pd.read_csv(path, header=None)

                    # data init
                    if not csv_data.empty:
                        data = pd.DataFrame(columns=[
                                                     'SalesDate',
                                                     'Line',
                                                     'Shift',
                                                     'OracleType',
                                                     'MIPS_Description',
                                                     'LostTimeMinutes',
                                                     'LostTimeValue',
                                                     'Occ',
                                                     'OracleCategory',
                                                     'Category',
                                                     'Area',
                                                     'Cause',
                                                     'Comments',
                                                     'LineStop',
                                                     'Init'
                                                     ])

                        data['SalesDate'] = csv_data[27]
                        data['Line'] = csv_data[28]
                        data['Shift'] = csv_data[29]
                        data['OracleType'] = csv_data[30]
                        data['MIPS_Description'] = csv_data[31]
                        data['LostTimeMinutes'] = csv_data[32]
                        data['LostTimeValue'] = csv_data[33]
                        data['Occ'] = csv_data[34]
                        data['OracleCategory'] = csv_data[35]
                        data['Category'] = csv_data[36]
                        data['Area'] = csv_data[37]
                        data['Cause'] = csv_data[38]
                        data['Comments'] = csv_data[39]
                        data['LineStop'] = csv_data[40]
                        data['Init'] = csv_data[41]

                        # mapping line and shift
                        line_mapping = {
                            'Line 1': '1',
                            'Line 2': '2',
                            'Line 7': '7',
                            'Line 8': '8',
                            'Line 9': '9',
                        }
                        shift_mapping = {
                            'Shift 1': '1',
                            'Shift 2': '2',
                            'Shift 3': '3',
                            'ZZZZ': 'N',
                        }
                        mapping = line_mapping.copy()
                        mapping.update(shift_mapping)
                        data.replace(mapping, inplace=True)
                        data['LostTimeValue'] = data['LostTimeValue'].str.replace('$', '')
                        data['LostTimeValue'] = data['LostTimeValue'].astype('float64')

                        data['SalesDate'] = pd.to_datetime(data['SalesDate'], format='%m/%d/%y', utc=True)

                        for index, row in data.iterrows():
                            ReportLostTimeDetail.objects \
                            .update_or_create(SalesDate=row['SalesDate'],
                                              Line=row['Line'],
                                              Shift=row['Shift'],
                                              MIPS_Description=row['MIPS_Description'],
                                              LostTimeMinutes=row['LostTimeMinutes'],
                                              defaults={
                                                         'LostTimeValue': row['LostTimeValue'],
                                                         'Occ': row['Occ'],
                                                         'OracleCategory': row['OracleCategory'],
                                                         'Category': row['Category'],
                                                         'Area': row['Area'],
                                                         'Cause': row['Cause'],
                                                         'Comments': row['Comments'],
                                                         'LineStop': row['LineStop'],
                                                         'Init': row['Init'],
                                                        })

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})

