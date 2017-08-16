import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt, timedelta
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse
from django.db.models import Q, Count, Min, Sum, Avg

from .models.models import *

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class FormManager:

            @classmethod
            def submit(cls, request, *args, **kwargs):
                start_date = request.GET.get('StartDate')
                end_date = request.GET.get('EndDate')
                start_shift = request.GET.get('StartShift')
                end_shift = request.GET.get('EndShift')
                line = request.GET.get('Line')

                StartDate = UDatetime.datetime_str_init(start_date)
                EndDate = UDatetime.datetime_str_init(end_date, StartDate, timedelta(days=0))

                response = []

                if EndDate > StartDate + timedelta(days=1):
                    print(1)
                    start_shift_range = UDatetime.pick_shift_by_start_shift(start_shift)
                    end_shift_range = UDatetime.pick_shift_by_end_shift(end_shift)
                    records = ReportTimeDetail.objects\
                        .filter(Q(SalesDate__range=[StartDate + timedelta(days=1), EndDate - timedelta(days=1)],
                                  Line__exact=line) |
                                Q(SalesDate__exact=StartDate, Line__exact=line, Shift__in=start_shift_range) |
                                Q(SalesDate__exact=EndDate, Line__exact=line, Shift__in=end_shift_range)
                                )
                elif EndDate == StartDate + timedelta(days=1):
                    start_shift_range = UDatetime.pick_shift_by_start_shift(start_shift)
                    end_shift_range = UDatetime.pick_shift_by_end_shift(end_shift)
                    records = ReportTimeDetail.objects\
                        .filter(Q(SalesDate__exact=StartDate, Line__exact=line, Shift__in=start_shift_range) |
                                Q(SalesDate__exact=EndDate, Line__exact=line, Shift__in=end_shift_range)
                                )
                elif EndDate == StartDate:
                    shift_range = UDatetime.pick_shift_by_two_shift(start_shift, end_shift)
                    records = ReportTimeDetail.objects.filter(SalesDate__range=[StartDate, EndDate],
                                                              Line__exact=line,
                                                              Shift__in=shift_range)
                else:
                    records = ReportTimeDetail.objects.none()

                if records.exists():
                    data = pd.DataFrame.from_records(records.values('SalesDate',
                                                                    'Line',
                                                                    'Shift',
                                                                    'MIPS_Description',
                                                                    'MechLostTime_min',
                                                                    'TotalLostTime_min'))

                    data = data[data['MechLostTime_min']!=0]
                    data_gp = data[['MIPS_Description', 'MechLostTime_min']]\
                        .groupby(['MIPS_Description'], as_index=False)['MechLostTime_min']\
                        .agg(['count', 'sum'])

                    data_gp.reset_index(inplace=True)
                    data_gp['colorIndex'] = 8
                    data_gp.rename_axis({'MIPS_Description': 'name', 'sum': 'y'}, axis=1, inplace=True)
                    data_gp.sort_values(['y'], ascending=[False], inplace=True)

                    total_sum = data_gp['y'].sum()
                    total_count = data_gp['count'].sum()
                    total = pd.DataFrame({'name': 'Total', 'colorIndex': 9, 'y': total_sum, 'count': total_count}, index=[0])
                    data_gp['y'] = -data_gp['y']
                    data_gp = total.append(data_gp, ignore_index=True)

                    response = data_gp.to_dict(orient='records')

                return JsonResponse(response, safe=False)