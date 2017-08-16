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


class ReportTimeDetailProcessor:

    @classmethod
    def report_time_detail_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='ReportTimeDetail')
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
                                                     'OracleFormula',
                                                     'MIPS_Description',
                                                     'SchedChangeOverTime_min',
                                                     'OracleTheoChangeOverTime_min',
                                                     'ActualChangeOverTime_min',
                                                     'Init',
                                                     'WrappingStartDateTime',
                                                     'WrappingEndDateTime',
                                                     'MechLostTime_min',
                                                     'SchedLostTime_min',
                                                     'AOLostTime_min',
                                                     'ActualRunTime_min',
                                                     'TotalLostTime_min',
                                                     'OracleAOLostTime_min',
                                                     'TheoRunTime_min',
                                                     'EngTheoRunTime_min',
                                                     'TimeVar_min',
                                                     'TimeVar_perc',
                                                     ])

                        data['SalesDate'] = csv_data[34]
                        data['Line'] = csv_data[32]
                        data['Shift'] = csv_data[33]
                        data['OracleType'] = csv_data[35]
                        data['OracleFormula'] = csv_data[36]
                        data['MIPS_Description'] = csv_data[37]
                        data['SchedChangeOverTime_min'] = csv_data[38]
                        data['OracleTheoChangeOverTime_min'] = csv_data[39]
                        data['ActualChangeOverTime_min'] = csv_data[40]
                        data['Init'] = csv_data[41]
                        data['WrappingStartDateTime'] = csv_data[42]
                        data['WrappingEndDateTime'] = csv_data[43]
                        data['MechLostTime_min'] = csv_data[44]
                        data['SchedLostTime_min'] = csv_data[45]
                        data['AOLostTime_min'] = csv_data[46]
                        data['ActualRunTime_min'] = csv_data[47]
                        data['TotalLostTime_min'] = csv_data[48]
                        data['OracleAOLostTime_min'] = csv_data[49]
                        data['TheoRunTime_min'] = csv_data[50]
                        data['EngTheoRunTime_min'] = csv_data[51]
                        data['TimeVar_min'] = csv_data[52]
                        data['TimeVar_perc'] = csv_data[53]

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

                        data['SalesDate'] = pd.to_datetime(data['SalesDate'], format='%m/%d/%y', utc=True)

                        for index, row in data.iterrows():
                            ReportTimeDetail.objects \
                            .update_or_create(SalesDate=row['SalesDate'],
                                              Line=row['Line'],
                                              Shift=row['Shift'],
                                              MIPS_Description=row['MIPS_Description'],
                                              TheoRunTime_min=row['TheoRunTime_min'],
                                              defaults={
                                                         # 'SalesDate': row['SalesDate'],
                                                         # 'Line': row['Line'],
                                                         # 'Shift': row['Shift'],
                                                         'OracleType': row['OracleType'],
                                                         'OracleFormula': row['OracleFormula'],
                                                         # 'MIPS_Description': row['SalesDate'],
                                                         'SchedChangeOverTime_min': row['SchedChangeOverTime_min'],
                                                         'OracleTheoChangeOverTime_min': row['OracleTheoChangeOverTime_min'],
                                                         'ActualChangeOverTime_min': row['ActualChangeOverTime_min'],
                                                         'Init': row['Init'],
                                                         'WrappingStartDateTime': row['WrappingStartDateTime'],
                                                         'WrappingEndDateTime': row['WrappingEndDateTime'],
                                                         'MechLostTime_min': row['MechLostTime_min'],
                                                         'SchedLostTime_min': row['SchedLostTime_min'],
                                                         'AOLostTime_min': row['AOLostTime_min'],
                                                         'ActualRunTime_min': row['ActualRunTime_min'],
                                                         'TotalLostTime_min': row['TotalLostTime_min'],
                                                         'OracleAOLostTime_min': row['OracleAOLostTime_min'],
                                                         # 'TheoRunTime_min': row['SalesDate'],
                                                         'EngTheoRunTime_min': row['EngTheoRunTime_min'],
                                                         'TimeVar_min': row['TimeVar_min'],
                                                         'TimeVar_perc': row['TimeVar_perc'],
                                                        })

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})

