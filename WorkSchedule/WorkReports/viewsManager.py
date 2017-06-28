from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from django.db.models import Q
from bbu.settings import TIME_ZONE

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *

EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class ModalManager:
            @staticmethod
            def extend_worker_avail(request, *args, **kwargs):
                worker_id = request.POST.get('resourceId')
                start = request.POST.get('start')
                end = request.POST.get('end')

                start = parse(start).replace(tzinfo=EST)
                end = parse(end).replace(tzinfo=EST)
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

                data = pd.DataFrame()
                if not data.empty:
                    response = data.to_dict(orient='records')
                    return JsonResponse(response, safe=False)
                else:
                    return JsonResponse({})

        class FormManager:
            @staticmethod
            def submit(request, *args, **kwargs):
                ReportType = request.GET.get('ReportType')
                start = request.GET.get('PeriodStart')
                end = request.GET.get('PeriodEnd')

                if start:
                    start = dt.strptime(start,'%Y-%m-%d').replace(tzinfo=EST)
                if end:
                    end = dt.strptime(end,'%Y-%m-%d').replace(tzinfo=EST)

                worker_scheduled = WorkerScheduled.objects.filter(time_start__gte=start, time_end__lte=end)
                if worker_scheduled.exists():
                    worker_scheduled_df = pd.DataFrame.from_records(worker_scheduled.values('name__name',
                                                                                            'date',
                                                                                            'task_id__work_order',
                                                                                            'task_id__priority',
                                                                                            'task_id__description',
                                                                                            'task_id__estimate_hour'))
                else:
                    worker_scheduled_df = pd.DataFrame()

                worker_scheduled_df.rename_axis({'name__name':'Mechanic',
                                                 'date':'date',
                                                 'task_id__work_order':'Work Order',
                                                 'task_id__priority':'Priority',
                                                 'task_id__description':'Description',
                                                 'task_id__estimate_hour':'EST'},inplace=True)

                print(worker_scheduled_df)


                return JsonResponse({})