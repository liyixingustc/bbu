from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from django.db.models import Q

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
                avail_events['color'] = 'light green'
                avail_events.rename_axis({'name__id': 'resourceId',
                                          'time_start': 'start',
                                          'time_end': 'end'},axis=1,inplace=True)

                avail_response = avail_events.to_dict(orient='records')

                response = []
                response += avail_response

                return JsonResponse(response,safe=False)

        class ModalManager:
            @staticmethod
            def extend_worker_avail(request, *args, **kwargs):
                worker_id = request.POST.get('resourceId')
                start = request.POST.get('start')
                end = request.POST.get('end')

                start = parse(start).replace(tzinfo=pytz.utc)
                end = parse(end).replace(tzinfo=pytz.utc)
                worker = Workers.objects.get(id=worker_id)

                avails = WorkerAvailable.objects.filter(Q(time_start__range=[start,end])|
                                                        Q(time_end__range=[start, end])|
                                                        Q(time_start__lte=start,time_end__gte=end),
                                                        name__exact=worker)

                if avails.exists():

                    avails_df = pd.DataFrame.from_records(avails.values())
                    start_list = avails_df['time_start'].tolist()
                    start_list.append(start)
                    end_list = avails_df['time_end'].tolist()
                    end_list.append(end)
                    start_new = min(start_list)
                    end_new = max(end_list)
                    duration_new = end_new - start_new
                    ids = avails_df['id'].tolist()

                    WorkerAvailable.objects.filter(id__in=ids).delete()
                    WorkerAvailable.objects.update_or_create(name=worker,
                                                             date=start_new.date(),
                                                             duration=duration_new,
                                                             time_start=start_new,
                                                             time_end=end_new)
                else:
                    duration=end-start
                    WorkerAvailable.objects.update_or_create(name=worker,
                                                             date=start.date(),
                                                             duration=duration,
                                                             time_start=start,
                                                             time_end=end)

                return JsonResponse({})

        class TableManager:
            @staticmethod
            def create(request, *args, **kwargs):

                tables_template_name = 'WorkScheduler/WorkScheduler_Panel2_Table1.html'
                data = WorkSchedulerPanel2Table1Manager.set_data()
                table = WorkSchedulerPanel2Table1(data)
                return render(request, tables_template_name, {'table': table})