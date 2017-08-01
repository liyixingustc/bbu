from django.http import JsonResponse
from django.shortcuts import render
import numpy as np
import pandas as pd
import pytz
from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.tz import tzlocal
from django.db.models import Q, Count, Min, Sum, Avg
from bbu.settings import TIME_ZONE

from django.db import models
from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *
from .tables.tables import *
from .tables.tablesManager import *
from utils.UDatetime import UDatetime

from DAO.WorkScheduleDataDAO import WorkScheduleDataDAO

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


                # workers_contractor_df = workers_contractor_df[workers_contractor_df['scheduled_hour'] > timedelta()]
                # print(workers_contractor_df)

                workers_df = WorkScheduleDataDAO.get_all_workers_by_date_range(start_date, end_date)

                response = []

                if not workers_df.empty:
                    workers_df.rename_axis({'name': 'title', 'balance': 'Avail'}, axis=1, inplace=True)
                    response = workers_df.to_dict(orient='records')
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
                                                                                  'time_end',
                                                                                  'date'
                                                                                  ))

                    avail_events['id'] = 'WorkerAvail'
                    avail_events['rendering'] = 'background'
                    avail_events['color'] = 'lightgreen'
                    avail_events.rename_axis({'name__id': 'resourceId',
                                              'time_start': 'start',
                                              'time_end': 'end'}, axis=1, inplace=True)
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
                                                                                   'task_id__AOR__equip_code',
                                                                                   'task_id__priority',
                                                                                   'task_id__estimate_hour',
                                                                                   'duration',
                                                                                   'time_start',
                                                                                   'time_end')
                                                              .annotate(total_duration=Sum('task_id__workerscheduled__duration')))
                    event_records.rename_axis({'id': 'workerscheduledId',
                                               'name__id': 'resourceId',
                                               'task_id__work_order': 'taskId',
                                               'task_id__description': 'description',
                                               'task_id__AOR__equip_code': 'equip_code',
                                               'task_id__priority': 'priority',
                                               'task_id__estimate_hour': 'est',
                                               'duration': 'duration',
                                               'time_start': 'start',
                                               'time_end': 'end'}, axis=1, inplace=True)
                    event_records['resourceId'] = event_records['resourceId'].astype('str')
                    event_records['title'] = event_records['taskId']
                    event_records['constraint'] = 'WorkerAvail'
                    event_records['percent'] = event_records['total_duration']/event_records['est']
                    event_records['percent'] = event_records['percent'].apply(lambda x: np.round(x, 2))
                    event_records['remaining_hours'] = event_records['est'] - event_records['duration']
                    event_records['remaining_hours'] = event_records['remaining_hours'].apply(lambda x:round(x.total_seconds()/3600))

                    event_records['start'] = event_records['start'].apply(lambda x: x.astimezone(EST))
                    event_records['end'] = event_records['end'].apply(lambda x: x.astimezone(EST))
                    event_records['duration'] = event_records['duration'].apply(lambda x: np.round(x.total_seconds()/3600, 2))

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

                task = Tasks.objects.get(work_order=taskId)

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=int(task.estimate_hour.total_seconds()/3600)))

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

                    worker_scheduled = WorkerScheduled.objects.update_or_create(name=worker,
                                                                                date=date,
                                                                                time_start=start,
                                                                                time_end=end,
                                                                                task_id=task,
                                                                                available_id=available_id,
                                                                                defaults={'duration': duration})

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
            def select_submit(request, *args, **kwargs):
                command_type = request.GET.get('CommandType')
                worker_id = request.GET.get('resourceId')
                start = request.GET.get('start')
                end = request.GET.get('end')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=2))

                date = UDatetime.pick_date_by_two_date(start, end)
                duration = end - start

                worker = Workers.objects.get(id=worker_id)
                if command_type == 'ExtendWorkerAvailable':
                    avails = WorkerAvailable.objects.filter(Q(time_start__range=[start, end]) |
                                                            Q(time_end__range=[start, end]) |
                                                            Q(time_start__lte=start, time_end__gte=end),
                                                            name__exact=worker)

                    if avails.exists():

                        avails_df = pd.DataFrame.from_records(avails.values())
                        if avails.count() == 1:
                            ids = avails_df['id'].tolist()
                        else:
                            ids = 1

                        start_list = avails_df['time_start'].tolist()
                        start_list.append(start)
                        end_list = avails_df['time_end'].tolist()
                        end_list.append(end)
                        start_new = min(start_list).astimezone(EST)
                        end_new = max(end_list).astimezone(EST)
                        date = UDatetime.pick_date_by_two_date(start_new, end_new)

                        duration_new = end_new - start_new

                        WorkerAvailable.objects.update_or_create(id__in=ids,
                                                                 defaults={
                                                                     'name': worker,
                                                                     'date': date,
                                                                     'duration': duration_new,
                                                                     'deduction': WorkAvailSheet.DEDUCTION,
                                                                     'time_start': start_new,
                                                                     'time_end': end_new
                                                                 })

                    else:
                        duration = end - start
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=start.date(),
                                                                 duration=duration,
                                                                 deduction=WorkAvailSheet.DEDUCTION,
                                                                 time_start=start,
                                                                 time_end=end,
                                                                 source='manual')

                elif command_type == 'CutWorkerAvailable':
                    avails = WorkerAvailable.objects.filter(Q(time_start__range=[start, end]) |
                                                            Q(time_end__range=[start, end]) |
                                                            Q(time_start__lte=start, time_end__gte=end),
                                                            name__exact=worker)

                    if avails.exists():
                        avails_df = pd.DataFrame.from_records(avails.values())
                        if avails.count() == 1:
                            ids = avails_df['id'].tolist()

                            start_list = avails_df['time_start'].tolist()
                            start_list.append(start)
                            end_list = avails_df['time_end'].tolist()
                            end_list.append(end)
                            range_new = UDatetime.remove_overlap(start_list[0], end_list[0], start_list[1], end_list[1])
                            if len(range_new) == 1:
                                start_new = range_new[0][0]
                                end_new = range_new[0][1]
                                if start_new == end_new:
                                    WorkerAvailable.objects.filter(id__in=ids).delete()
                                else:
                                    date = UDatetime.pick_date_by_two_date(start_new, end_new)

                                    duration_new = end_new - start_new

                                    WorkerAvailable.objects.update_or_create(id__in=ids,
                                                                             defaults={
                                                                                 'name': worker,
                                                                                 'date': date,
                                                                                 'duration': duration_new,
                                                                                 'deduction': WorkAvailSheet.DEDUCTION,
                                                                                 'time_start': start_new,
                                                                                 'time_end': end_new
                                                                             })
                            else:
                                return JsonResponse({})

                elif command_type in ['Lunch', 'Breaks', 'UnionBus']:
                    if command_type == 'Lunch':
                        task = Tasks.objects.get(work_order__exact='0')
                    elif command_type == 'Breaks':
                        task = Tasks.objects.get(work_order__exact='1')
                    elif command_type == 'UnionBus':
                        task = Tasks.objects.get(work_order__exact='10')
                    else:
                        task = Tasks.objects.get(work_order__exact='0')

                    available_ids = WorkerAvailable.objects.filter(time_start__lte=start,
                                                                  time_end__gte=end,
                                                                  name__exact=worker)
                    if available_ids.count() > 0:
                        available_id = available_ids[0]

                        worker_scheduled = WorkerScheduled.objects.update_or_create(name=worker,
                                                                                    date=date,
                                                                                    time_start=start,
                                                                                    time_end=end,
                                                                                    task_id=task,
                                                                                    available_id=available_id,
                                                                                    defaults={'duration': duration})




                return JsonResponse({})

            @staticmethod
            def tasks_submit(request, *args, **kwargs):
                command_type = request.GET.get('CommandType')
                start = request.GET.get('start')
                end = request.GET.get('end')
                resourceId = request.GET.get('resourceId')
                taskId = request.GET.get('taskId')
                workerscheduledId = request.GET.get('workerscheduledId')

                if command_type == 'Revise':
                    WorkerScheduled.objects.filter(id__exact=workerscheduledId).update()
                elif command_type == 'Remove':
                    WorkerScheduled.objects.filter(id__exact=workerscheduledId).delete()

                response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def add_worker_submit(request, *args, **kwargs):
                print(request)
                response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def worker_submit(request, *args, **kwargs):

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

            @staticmethod
            def edit(request, *args, **kwargs):

                estimate_hour = request.GET.get('estimate_hour')
                work_order = request.GET.get('work_order')

                estimate_hour = timedelta(hours=float(estimate_hour))

                Tasks.objects.filter(work_order__exact=work_order).update(estimate_hour=estimate_hour)

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
                print(start_date,end_date)

                worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
                worker_scheduled = WorkerScheduled.objects.filter(date__range=[start_date, end_date])

                tasks_all = Tasks.objects.filter(Q(current_status__in=['new', 'pending']) |
                                                 Q(kitted_date__range=[start, end], current_status__in=['completed']))

                tasks = Tasks.objects.filter(Q(current_status__in=['new', 'pending']))\
                                     .exclude(priority__in=['T', 'O'])\
                                     .annotate(scheduled_hour=Sum('workerscheduled__duration'))

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
                    tasks_df = pd.DataFrame.from_records(tasks.values('estimate_hour', 'scheduled_hour'))
                    tasks_est = tasks_df['estimate_hour'].sum().total_seconds() / 3600
                    tasks_count = len(tasks_df)
                    tasks_scheduled_count = len(tasks_df[~tasks_df['scheduled_hour'].isnull()])
                else:
                    tasks_est = 0
                    tasks_count = 0
                    tasks_scheduled_count = 0

                avail_remain = avail - scheduled
                task_est_remain = tasks_est - scheduled

                response = {
                            'scheduled': scheduled,
                            'avail': avail,
                            'avail_remain': avail_remain,
                            'tasks_est': tasks_est,
                            'task_est_remain': task_est_remain,
                            'tasks_count': tasks_count,
                            'tasks_scheduled_count': tasks_scheduled_count
                }

                return JsonResponse(response)

