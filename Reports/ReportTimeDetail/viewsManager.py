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
                groupby = request.GET.get('GroupBy')
                product_name = request.GET.get('product_name')
                cause_name = request.GET.get('cause_name')
                div_id = request.GET.get('div_id')

                StartDate = UDatetime.datetime_str_init(start_date)
                EndDate = UDatetime.datetime_str_init(end_date, StartDate, timedelta(days=0))

                response = []

                if EndDate > StartDate + timedelta(days=1):
                    start_shift_range = UDatetime.pick_shift_by_start_shift(start_shift)
                    end_shift_range = UDatetime.pick_shift_by_end_shift(end_shift)
                    records = ReportLostTimeDetail.objects\
                        .filter(Q(SalesDate__range=[StartDate + timedelta(days=1), EndDate - timedelta(days=1)],
                                  Line__exact=line) |
                                Q(SalesDate__exact=StartDate, Line__exact=line, Shift__in=start_shift_range) |
                                Q(SalesDate__exact=EndDate, Line__exact=line, Shift__in=end_shift_range)
                                )
                elif EndDate == StartDate + timedelta(days=1):
                    start_shift_range = UDatetime.pick_shift_by_start_shift(start_shift)
                    end_shift_range = UDatetime.pick_shift_by_end_shift(end_shift)
                    records = ReportLostTimeDetail.objects\
                        .filter(Q(SalesDate__exact=StartDate, Line__exact=line, Shift__in=start_shift_range) |
                                Q(SalesDate__exact=EndDate, Line__exact=line, Shift__in=end_shift_range)
                                )
                elif EndDate == StartDate:
                    shift_range = UDatetime.pick_shift_by_two_shift(start_shift, end_shift)
                    records = ReportLostTimeDetail.objects.filter(SalesDate__range=[StartDate, EndDate],
                                                              Line__exact=line,
                                                              Shift__in=shift_range)
                else:
                    records = ReportLostTimeDetail.objects.none()

                if records.exists():
                    data = pd.DataFrame.from_records(records.values('SalesDate',
                                                                    'Line',
                                                                    'Shift',
                                                                    'MIPS_Description',
                                                                    'Cause',
                                                                    'Comments',
                                                                    'LostTimeMinutes',
                                                                    'Occ'))

                    data = data[data['LostTimeMinutes'] != 0]
                    # get the for lower leven when click on the bar
                    if groupby == 'Product':
                        if div_id == 'ReportLostTimeDetailPanel2Chart1' and product_name and product_name != 'Total':
                            groupby = 'Cause'
                            data = data[data['MIPS_Description'] == product_name]
                        elif div_id == 'ReportLostTimeDetailPanel2Chart2' and cause_name and cause_name != 'Total':
                            groupby = 'Comments'
                            data = data[(data['MIPS_Description'] == product_name) & (data['Cause'] == cause_name)]
                    elif groupby == 'Cause':
                        if div_id == 'ReportLostTimeDetailPanel2Chart2' and cause_name and cause_name != 'Total':
                            groupby = 'Comments'
                            data = data[data['Cause'] == cause_name]

                    # group data by different groupby field
                    if groupby == 'Product':
                        data_gp = data[['MIPS_Description', 'LostTimeMinutes', 'Occ']]\
                            .groupby(['MIPS_Description'], as_index=False)['LostTimeMinutes', 'Occ']\
                            .agg('sum')
                        data_gp.rename_axis({'MIPS_Description': 'name', 'LostTimeMinutes': 'y', 'Occ': 'count'},
                                            axis=1, inplace=True)
                    elif groupby == 'Cause':
                        data_gp = data[['Cause', 'LostTimeMinutes', 'Occ']]\
                            .groupby(['Cause'], as_index=False)['LostTimeMinutes', 'Occ']\
                            .agg('sum')
                        data_gp.rename_axis({'Cause': 'name', 'LostTimeMinutes': 'y', 'Occ': 'count'},
                                            axis=1, inplace=True)
                    elif groupby == 'Comments':
                        data_gp = data[['Comments', 'LostTimeMinutes', 'Occ']]\
                            .groupby(['Comments'], as_index=False)['LostTimeMinutes', 'Occ']\
                            .agg('sum')
                        data_gp.rename_axis({'Comments': 'name', 'LostTimeMinutes': 'y', 'Occ': 'count'},
                                            axis=1, inplace=True)
                    else:
                        response = []
                        return JsonResponse(response, safe=False)

                    data_gp.reset_index(inplace=True, drop=True)
                    data_gp['colorIndex'] = 8
                    data_gp.sort_values(['y'], ascending=[False], inplace=True)

                    total_sum = data_gp['y'].sum()
                    total_count = data_gp['count'].sum()
                    total = pd.DataFrame({'name': 'Total', 'colorIndex': 9, 'y': total_sum, 'count': total_count}, index=[0])
                    data_gp['y'] = -data_gp['y']
                    data_gp = total.append(data_gp, ignore_index=True)

                    response = data_gp.to_dict(orient='records')

                return JsonResponse(response, safe=False)