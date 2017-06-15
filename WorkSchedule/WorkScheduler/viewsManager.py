from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
from datetime import datetime as dt

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *
from .tables.tables import *
from .tables.tablesManager import *


class PageManager:
    class PanelManager:
        class TimeLineManager:
            @staticmethod
            def resources(request, *args, **kwargs):
                start = request.GET.get('start')
                workers = Workers.objects.all().values()
                records = pd.DataFrame.from_records(workers)
                records.rename_axis({'name':'title'},axis=1,inplace=True)
                response = records.to_dict(orient='records')
                return JsonResponse(response,safe=False)

            @staticmethod
            def events(request, *args, **kwargs):
                start = request.GET.get('start')
                end = request.GET.get('end')
                start = dt.strptime(start, '%Y-%m-%d')
                end = dt.strptime(end, '%Y-%m-%d')

                # avail events
                avail_records = WorkerAvailable.objects.filter(date__range=[start.date(), end.date()])
                avail_events = pd.DataFrame.from_records(avail_records.values('name__id',
                                                                              'time_start',
                                                                              'time_end'))

                avail_events['rendering'] = 'background'
                avail_events['color'] = 'green'
                avail_events.rename_axis({'name__id': 'resourceId',
                                          'time_start': 'start',
                                          'time_end': 'end'},axis=1,inplace=True)

                avail_response = avail_events.to_dict(orient='records')

                response = []
                response += avail_response

                return JsonResponse(response,safe=False)
        class TableManager:
            @staticmethod
            def create(request, *args, **kwargs):

                tables_template_name = 'WorkScheduler/WorkScheduler_Panel2_Table1.html'
                data = WorkSchedulerPanel2Table1Manager.set_data()
                table = WorkSchedulerPanel2Table1(data)
                return render(request, tables_template_name, {'table': table})