from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q
from bbu.settings import TIME_ZONE

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *
from .tables.tables import *
from .tables.tablesManager import *

EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class TimeLineManager:
            @staticmethod
            def resources(request, *args, **kwargs):
                start = request.GET.get('start')
                end = request.GET.get('end')

                if start:
                    start = dt.strptime(start,'%Y-%m-%d').replace(tzinfo=EST)
                if end:
                    end = dt.strptime(end,'%Y-%m-%d').replace(tzinfo=EST)

                workers = Workers.objects.all()
                response = []

                if workers.exists():
                    workers = pd.DataFrame.from_records(workers.values('id','name'))
                    workers['id'] = workers['id'].astype('str')

                    worker_avail = WorkerAvailable.objects.filter(time_start__gte=start,time_end__lte=end)
                    worker_scheduled = WorkerScheduled.objects.filter(time_start__gte=start,time_end__lte=end)

                    for index,row in workers.iterrows():
                        if worker_avail.exists():
                            worker_avail_df = pd.DataFrame.from_records(worker_avail.values('name', 'duration'))
                            avail = worker_avail_df[worker_avail_df['name'] == row['name']]['duration']
                            avail = avail.sum()
                            # print(avail)
                        else:
                            avail = timedelta(hours=0)
                        if worker_scheduled.exists():
                            worker_scheduled_df = pd.DataFrame.from_records(worker_scheduled.values('name', 'duration'))
                            scheduled = worker_scheduled_df[worker_scheduled_df['name'] == row['name']]['duration']
                            scheduled = scheduled.sum()
                        else:
                            scheduled = timedelta(hours=0)
                            # print(scheduled)

                        balance = avail - scheduled
                        workers.set_value(index, 'Avail', float(balance.total_seconds()/3600))

                    workers.rename_axis({'name':'title'},axis=1,inplace=True)

                    response = workers.to_dict(orient='records')
                    return JsonResponse(response,safe=False)
                else:
                    return JsonResponse(response,safe=False)

            @staticmethod
            def events(request, *args, **kwargs):
                start = request.GET.get('start')
                end = request.GET.get('end')
                start = dt.strptime(start, '%Y-%m-%d')
                end = dt.strptime(end, '%Y-%m-%d')

                # avail events
                avail_records = WorkerAvailable.objects.filter(date__range=[start.date(), end.date()])
                if avail_records.exists():
                    avail_events = pd.DataFrame.from_records(avail_records.values('name__id',
                                                                                  'time_start',
                                                                                  'time_end'))

                    avail_events['id'] = 'WorkerAvail'
                    avail_events['rendering'] = 'background'
                    avail_events['color'] = 'lightgreen'
                    avail_events.rename_axis({'name__id': 'resourceId',
                                              'time_start': 'start',
                                              'time_end': 'end'},axis=1,inplace=True)
                    avail_events['resourceId'] = avail_events['resourceId'].astype('str')

                    avail_response = avail_events.to_dict(orient='records')
                else:
                    avail_response = []

                # task events
                event_records = WorkerScheduled.objects.filter(date__range=[start.date(), end.date()])
                if event_records.exists():
                    event_records = pd.DataFrame.from_records(event_records.values('id',
                                                                                   'name__id',
                                                                                   'task_id__work_order',
                                                                                   'task_id__description',
                                                                                   'task_id__priority',
                                                                                   'task_id__estimate_hour',
                                                                                   'duration',
                                                                                   'time_start',
                                                                                   'time_end'))
                    event_records.rename_axis({'id': 'workerscheduledId',
                                               'name__id': 'resourceId',
                                               'task_id__work_order': 'taskId',
                                               'task_id__description': 'description',
                                               'task_id__priority': 'priority',
                                               'task_id__estimate_hour': 'est',
                                               'duration': 'duration',
                                               'time_start': 'start',
                                               'time_end': 'end'}, axis=1, inplace=True)
                    event_records['resourceId'] = event_records['resourceId'].astype('str')
                    event_records['title'] = event_records['taskId']
                    event_records['constraint'] = 'WorkerAvail'
                    event_records['percent'] = event_records['duration']/event_records['est']
                    event_records['percent'] = event_records['percent'].apply(lambda x: np.round(x, 2))
                    event_records['remaining_hours'] = event_records['est'] - event_records['duration']
                    event_records['remaining_hours'] = event_records['remaining_hours'].apply(lambda x:round(x.total_seconds()/3600))

                    event_records = event_records.to_dict(orient='records')
                else:
                    event_records = []

                response = []
                response += avail_response
                response += event_records

                return JsonResponse(response,safe=False)

            @staticmethod
            def event_create(request, *args, **kwargs):

                start = request.GET.get('start')
                end = request.GET.get('end')
                resourceId = request.GET.get('resourceId')
                taskId = request.GET.get('taskId')

                if start:
                    start = parse(start).replace(tzinfo=EST)
                if end:
                    end = parse(end).replace(tzinfo=EST)
                else:
                    end = start + timedelta(hours=2)

                duration = end - start

                worker = Workers.objects.get(id__exact=resourceId)
                task = Tasks.objects.get(work_order__exact=taskId)

                worker_scheduled = WorkerScheduled.objects.update_or_create(name=worker,
                                                                            date=start.date(),
                                                                            time_start=start,
                                                                            time_end=end,
                                                                            task_id=task,
                                                                            defaults={'duration': duration})

                print(start, end, resourceId, taskId)

                response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def event_update(request, *args, **kwargs):

                start = request.GET.get('start')
                end = request.GET.get('end')
                resourceId = request.GET.get('resourceId')
                taskId = request.GET.get('taskId')
                workerscheduledId = request.GET.get('workerscheduledId')
                print(start,end)
                if start:
                    start = parse(start).replace(tzinfo=EST)
                if end:
                    end = parse(end).replace(tzinfo=EST)
                else:
                    end = start + timedelta(hours=2)
                print(start,end)
                duration = end - start

                worker = Workers.objects.get(id__exact=resourceId)
                task = Tasks.objects.get(work_order__exact=taskId)

                WorkerScheduled.objects.filter(id__exact=workerscheduledId).update(name=worker,
                                                                                   date=start.date(),
                                                                                   duration=duration,
                                                                                   time_start=start,
                                                                                   time_end=end,
                                                                                   task_id=task
                                                                                   )

                # print(start,end,resourceId,taskId)

                response = []

                return JsonResponse(response,safe=False)

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

                data = WorkSchedulerPanel2Table1Manager.set_data()
                if not data.empty:
                    response = data.to_dict(orient='records')
                    return JsonResponse(response, safe=False)
                else:
                    return JsonResponse({})

        class KPIBoardManager:
            @staticmethod
            def update(request, *args, **kwargs):

                start = request.GET.get('start')
                end = request.GET.get('end')

                if start:
                    start = dt.strptime(start,'%Y-%m-%d').replace(tzinfo=EST)
                if end:
                    end = dt.strptime(end,'%Y-%m-%d').replace(tzinfo=EST)

                worker_avail = WorkerAvailable.objects.filter(time_start__gte=start, time_end__lte=end)
                worker_scheduled = WorkerScheduled.objects.filter(time_start__gte=start, time_end__lte=end)
                tasks = Tasks.objects.filter(Q(current_status__in=['new', 'pending']) |
                                             Q(create_on__range=[start, end], current_status__in=['completed']))

                if worker_avail.exists():
                    worker_avail_df = pd.DataFrame.from_records(worker_avail.values('duration'))
                    avail = worker_avail_df['duration'].sum().total_seconds() / 3600
                else:
                    avail = 0
                if worker_scheduled.exists():
                    worker_scheduled_df = pd.DataFrame.from_records(worker_scheduled.values('duration'))
                    scheduled = worker_scheduled_df['duration'].sum().total_seconds() / 3600
                else:
                    scheduled = 0
                if tasks.exists():
                    tasks_df = pd.DataFrame.from_records(tasks.values('estimate_hour'))
                    tasks_est = tasks_df['estimate_hour'].sum().total_seconds() / 3600
                else:
                    tasks_est = 0

                avail_remain = avail - scheduled
                task_remain = tasks_est - scheduled

                response = {'avail': avail,
                            'scheduled': scheduled,
                            'avail_remain': avail_remain,
                            'task_remain': task_remain}

                return JsonResponse(response)

