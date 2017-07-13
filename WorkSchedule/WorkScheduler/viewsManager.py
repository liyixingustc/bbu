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
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class TimeLineManager:
            @staticmethod
            def resources(request, *args, **kwargs):
                start = request.GET.get('start')
                end = request.GET.get('end')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(days=1))

                start_date = UDatetime.pick_date_by_one_date(start)
                end_date = UDatetime.pick_date_by_one_date(end)

                workers = Workers.objects.all()
                response = []

                if workers.exists():
                    workers = pd.DataFrame.from_records(workers.values('id','name'))
                    workers['id'] = workers['id'].astype('str')

                    worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
                    worker_scheduled = WorkerScheduled.objects.filter(date__range=[start_date, end_date])

                    for index, row in workers.iterrows():

                        avail = timedelta(hours=0)
                        avail_deduct = timedelta(hours=0)
                        if worker_avail.exists():
                            worker_avail_df = pd.DataFrame.from_records(worker_avail.values('name',
                                                                                            'duration',
                                                                                            'deduction',
                                                                                            'time_start',
                                                                                            'time_end'))
                            avail_df = worker_avail_df[worker_avail_df['name'] == row['name']]

                            for index_avail, row_avail in avail_df.iterrows():
                                avail += UDatetime.get_overlap(start, end,
                                                               row_avail['time_start'],
                                                               row_avail['time_end'])
                                avail_deduct += row_avail['deduction']

                        scheduled = timedelta(hours=0)
                        scheduled_deduct = timedelta(hours=0)
                        if worker_scheduled.exists():
                            worker_scheduled_df = pd.DataFrame.from_records(worker_scheduled.values('name',
                                                                                                    'duration',
                                                                                                    'deduction',
                                                                                                    'time_start',
                                                                                                    'time_end'))
                            scheduled_df = worker_scheduled_df[worker_scheduled_df['name'] == row['name']]

                            for index_scheduled, row_scheduled in scheduled_df.iterrows():
                                scheduled += UDatetime.get_overlap(start, end,
                                                                   row_scheduled['time_start'],
                                                                   row_scheduled['time_end'])
                                scheduled_deduct += row_scheduled['deduction']

                        balance = avail - scheduled - max(avail_deduct - scheduled_deduct, timedelta(hours=0))

                        workers.set_value(index, 'Avail', np.round((balance.total_seconds()/3600), 1))

                    workers.rename_axis({'name': 'title'}, axis=1, inplace=True)
                    response = workers.to_dict(orient='records')
                    return JsonResponse(response, safe=False)
                else:
                    return JsonResponse(response, safe=False)

            @staticmethod
            def events(request, *args, **kwargs):
                start = request.GET.get('start')
                end = request.GET.get('end')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(days=1))

                start_date = UDatetime.pick_date_by_one_date(start)
                end_date = UDatetime.pick_date_by_one_date(end)

                # avail events
                avail_records = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
                if avail_records.exists():
                    avail_events = pd.DataFrame.from_records(avail_records.values('name__id',
                                                                                  'time_start',
                                                                                  'time_end'))

                    avail_events['id'] = 'WorkerAvail'
                    avail_events['rendering'] = 'background'
                    avail_events['color'] = 'lightgreen'
                    avail_events.rename_axis({'name__id': 'resourceId',
                                              'time_start': 'start',
                                              'time_end': 'end'},axis=1, inplace=True)
                    avail_events['resourceId'] = avail_events['resourceId'].astype('str')
                    avail_events['start'] = avail_events['start'].apply(lambda x: x.astimezone(EST))
                    avail_events['end'] = avail_events['end'].apply(lambda x: x.astimezone(EST))

                    avail_response = avail_events.to_dict(orient='records')
                else:
                    avail_response = []

                # task events
                event_records = WorkerScheduled.objects.filter(date__range=[start_date, end_date])

                if event_records.exists():
                    event_records = pd.DataFrame.from_records(event_records.values('id',
                                                                                   'name__id',
                                                                                   'task_id__work_order',
                                                                                   'task_id__description',
                                                                                   'task_id__priority',
                                                                                   'task_id__estimate_hour',
                                                                                   'duration',
                                                                                   'deduction',
                                                                                   'time_start',
                                                                                   'time_end'))
                    event_records.rename_axis({'id': 'workerscheduledId',
                                               'name__id': 'resourceId',
                                               'task_id__work_order': 'taskId',
                                               'task_id__description': 'description',
                                               'task_id__priority': 'priority',
                                               'task_id__estimate_hour': 'est',
                                               'duration': 'duration',
                                               'deduction': 'deduction',
                                               'time_start': 'start',
                                               'time_end': 'end'}, axis=1, inplace=True)
                    event_records['resourceId'] = event_records['resourceId'].astype('str')
                    event_records['title'] = event_records['taskId']
                    event_records['constraint'] = 'WorkerAvail'
                    event_records['percent'] = (event_records['duration'] - event_records['deduction'])/event_records['est']
                    event_records['percent'] = event_records['percent'].apply(lambda x: np.round(x, 2))
                    event_records['remaining_hours'] = event_records['est'] - event_records['duration'] + event_records['deduction']
                    event_records['remaining_hours'] = event_records['remaining_hours'].apply(lambda x:round(x.total_seconds()/3600))

                    event_records['start'] = event_records['start'].apply(lambda x: x.astimezone(EST))
                    event_records['end'] = event_records['end'].apply(lambda x: x.astimezone(EST))
                    event_records['duration'] = event_records['duration'].apply(lambda x: round(x.total_seconds()/3600))
                    event_records['deduction'] = event_records['deduction'].apply(lambda x: round(x.total_seconds()/3600, 2))

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

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=2))

                date = UDatetime.pick_date_by_two_date(start, end)

                print(start,end)

                duration = end - start

                worker = Workers.objects.get(id__exact=resourceId)
                task = Tasks.objects.get(work_order__exact=taskId)
                available_ids = WorkerAvailable.objects.filter(time_start__lte=start,
                                                              time_end__gte=end,
                                                              name__exact=worker)
                if available_ids.count() > 0:
                    available_id = available_ids[0]
                    work_scheduled = WorkerScheduled.objects.filter(available_id__exact=available_id)

                    if work_scheduled.exists():

                        work_scheduled_df = pd.DataFrame.from_records(work_scheduled.values('deduction',
                                                                                            'available_id__deduction'))
                        scheduled_deduction_former = work_scheduled_df['deduction'].sum()
                        available_deduction_former = work_scheduled_df['available_id__deduction'].sum()
                        deduction = max(available_deduction_former - scheduled_deduction_former, timedelta(hours=0))
                    else:
                        deduction = available_id.deduction

                    worker_scheduled = WorkerScheduled.objects.update_or_create(name=worker,
                                                                                date=date,
                                                                                time_start=start,
                                                                                time_end=end,
                                                                                task_id=task,
                                                                                available_id=available_id,
                                                                                defaults={'duration': duration,
                                                                                          'deduction': deduction})


                response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def event_update(request, *args, **kwargs):

                start = request.GET.get('start')
                end = request.GET.get('end')
                resourceId = request.GET.get('resourceId')
                taskId = request.GET.get('taskId')
                workerscheduledId = request.GET.get('workerscheduledId')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=2))

                date = UDatetime.pick_date_by_two_date(start, end)

                duration = end - start

                worker = Workers.objects.get(id__exact=resourceId)
                task = Tasks.objects.get(work_order__exact=taskId)
                available_id = WorkerAvailable.objects.filter(time_start__lte=start,
                                                              time_end__gte=end,
                                                              name__exact=worker)
                if available_id.count() > 0:
                    available_id = available_id[0]

                WorkerScheduled.objects.filter(id__exact=workerscheduledId).update(name=worker,
                                                                                   date=date,
                                                                                   duration=duration,
                                                                                   time_start=start,
                                                                                   time_end=end,
                                                                                   task_id=task,
                                                                                   available_id=available_id
                                                                                   )

                response = []

                return JsonResponse(response,safe=False)

        class ModalManager:
            @staticmethod
            def extend_worker_avail(request, *args, **kwargs):
                worker_id = request.POST.get('resourceId')
                start = request.POST.get('start')
                end = request.POST.get('end')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=2))

                worker = Workers.objects.get(id=worker_id)

                avails = WorkerAvailable.objects.filter(Q(time_start__range=[start, end]) |
                                                        Q(time_end__range=[start, end]) |
                                                        Q(time_start__lte=start, time_end__gte=end),
                                                        name__exact=worker)

                if avails.exists():

                    avails_df = pd.DataFrame.from_records(avails.values())

                    start_list = avails_df['time_start'].tolist()
                    start_list.append(start)
                    end_list = avails_df['time_end'].tolist()
                    end_list.append(end)
                    start_new = min(start_list).astimezone(EST)
                    end_new = max(end_list).astimezone(EST)
                    date = UDatetime.pick_date_by_two_date(start_new, end_new)

                    duration_new = end_new - start_new
                    ids = avails_df['id'].tolist()

                    WorkerAvailable.objects.filter(id__in=ids).delete()
                    WorkerAvailable.objects.update_or_create(name=worker,
                                                             date=date,
                                                             duration=duration_new,
                                                             time_start=start_new,
                                                             time_end=end_new)
                else:
                    duration = end - start
                    WorkerAvailable.objects.update_or_create(name=worker,
                                                             date=start.date(),
                                                             duration=duration,
                                                             deduction=timedelta(hours=1),
                                                             time_start=start,
                                                             time_end=end)

                return JsonResponse({})

            @staticmethod
            def tasks_submit(request, *args, **kwargs):
                command_type = request.GET.get('CommandType')
                start = request.GET.get('start')
                end = request.GET.get('end')
                resourceId = request.GET.get('resourceId')
                taskId = request.GET.get('taskId')
                workerscheduledId = request.GET.get('workerscheduledId')
                deduction = request.GET.get('Deduction')

                if command_type == 'Revise':
                    deduction = timedelta(hours=float(deduction))
                    WorkerScheduled.objects.filter(id__exact=workerscheduledId).update(deduction=deduction)
                elif command_type == 'Remove':
                    WorkerScheduled.objects.filter(id__exact=workerscheduledId).delete()

                response = []

                return JsonResponse(response, safe=False)

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

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(days=1))

                start_date = UDatetime.pick_date_by_one_date(start)
                end_date = UDatetime.pick_date_by_one_date(end)

                worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
                worker_scheduled = WorkerScheduled.objects.filter(date__range=[start_date, end_date])

                tasks = Tasks.objects.filter(Q(current_status__in=['new', 'pending']) |
                                             Q(create_on__range=[start, end], current_status__in=['completed']))

                if worker_avail.exists():
                    worker_avail_df = pd.DataFrame.from_records(worker_avail.values('duration', 'deduction'))

                    avail = (worker_avail_df['duration']-worker_avail_df['deduction']).sum().total_seconds() / 3600
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
                    tasks_count = len(tasks_df)
                else:
                    tasks_est = 0
                    tasks_count = 0

                avail_remain = avail - scheduled
                task_remain = tasks_est - scheduled

                response = {'avail': avail,
                            'scheduled': scheduled,
                            'avail_remain': avail_remain,
                            'task_remain': task_remain,
                            'tasks_count': tasks_count}

                return JsonResponse(response)

