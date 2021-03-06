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
from DAO.WorkScheduleReviseDAO import WorkScheduleReviseDAO

from .utils.SmartScheduler import SmartScheduler
from spider.somax.somax_spider import SomaxSpider
from spider.somax.tasks import *

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

                workers_df = WorkScheduleDataDAO.get_all_include_workers_by_date_range(start_date, end_date)
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
                    # avail_events['start'] = avail_events['start'].apply(lambda x: x.astimezone(EST))
                    # avail_events['end'] = avail_events['end'].apply(lambda x: x.astimezone(EST))

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

                    # event_records['start'] = event_records['start'].apply(lambda x: x.astimezone(EST))
                    # event_records['end'] = event_records['end'].apply(lambda x: x.astimezone(EST))
                    event_records['duration'] = event_records['duration'].apply(lambda x: np.round(x.total_seconds()/3600, 2))

                    # revise time off event percent
                    event_records[event_records['priority'] == 'T']['percent'] = 1

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

                print(start, end)

                duration = end - start

                worker = Workers.objects.get(id__exact=resourceId)
                task = Tasks.objects.get(work_order__exact=taskId)
                available_ids = WorkerAvailable.objects.filter(time_start__lte=start,
                                                               time_end__gte=end,
                                                               name__exact=worker)
                if available_ids.count() > 0:
                    available_id = available_ids[0]
                    WorkScheduleReviseDAO.update_or_create_schedule(request.user, start, end, date, duration,
                                                                    available_id, worker, task)

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

                WorkScheduleReviseDAO.update_or_create_schedule(request.user, start, end, date, duration,
                                                                available_id, worker, task,
                                                                schedule_id=workerscheduledId)

                response = []

                return JsonResponse(response,safe=False)

            @staticmethod
            def syc_tasks_from_somax(request, *args, **kwargs):
                response = []
                # SomaxSpider().task_spider()
                sync_task.delay()
                return JsonResponse(response, safe=False)

            @staticmethod
            def syc_tasks_to_somax(request, *args, **kwargs):
                response = []
                SomaxScheduleSpider().sync_schedules_to_somax_spider()
                # sync_schedules_to_somax.delay()
                return JsonResponse(response, safe=False)

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

                response = {}

                worker = Workers.objects.get(id=worker_id)
                if command_type == 'ExtendWorkerAvailable':
                    avails = WorkerAvailable.objects.filter(Q(time_start__range=[start, end]) |
                                                            Q(time_end__range=[start, end]) |
                                                            Q(time_start__lte=start, time_end__gte=end),
                                                            name__exact=worker)

                    if avails.exists():

                        avails_df = pd.DataFrame.from_records(avails.values())
                        if avails.count() == 1:
                            avail_id = avails_df['id'].tolist()[0]
                        else:
                            return

                        start_list = avails_df['time_start'].tolist()
                        start_list.append(start)
                        end_list = avails_df['time_end'].tolist()
                        end_list.append(end)
                        # start_new = min(start_list).astimezone(EST)
                        # end_new = max(end_list).astimezone(EST)
                        start_new = min(start_list).replace(tzinfo=EST)
                        end_new = max(end_list).replace(tzinfo=EST)
                        date = UDatetime.pick_date_by_two_date(start_new, end_new)

                        duration_new = end_new - start_new

                        WorkScheduleReviseDAO.update_or_create_available(request.user,
                                                                         start_new,
                                                                         end_new,
                                                                         date,
                                                                         duration_new,
                                                                         WorkAvailSheet.DEDUCTION,
                                                                         worker,
                                                                         avail_id=avail_id,
                                                                         source='manual')
                        # WorkerAvailable.objects.update_or_create(id=avail_id,
                        #                                          defaults={
                        #                                              'name': worker,
                        #                                              'date': date,
                        #                                              'duration': duration_new,
                        #                                              'deduction': WorkAvailSheet.DEDUCTION,
                        #                                              'time_start': start_new,
                        #                                              'time_end': end_new
                        #                                          })

                    else:
                        duration = end - start
                        WorkScheduleReviseDAO.update_or_create_available(request.user,
                                                                         start,
                                                                         end,
                                                                         start.date(),
                                                                         duration,
                                                                         WorkAvailSheet.DEDUCTION,
                                                                         worker,
                                                                         source='manual')
                        # WorkerAvailable.objects.update_or_create(name=worker,
                        #                                          date=start.date(),
                        #                                          duration=duration,
                        #                                          deduction=WorkAvailSheet.DEDUCTION,
                        #                                          time_start=start,
                        #                                          time_end=end,
                        #                                          source='manual')

                elif command_type == 'CutWorkerAvailable':
                    avails = WorkerAvailable.objects.filter(Q(time_start__range=[start, end]) |
                                                            Q(time_end__range=[start, end]) |
                                                            Q(time_start__lte=start, time_end__gte=end),
                                                            name__exact=worker)

                    if avails.exists():

                        start = start.replace(tzinfo=pytz.UTC)
                        end = end.replace(tzinfo=pytz.UTC)

                        avails_df = pd.DataFrame.from_records(avails.values())
                        if avails.count() == 1:
                            avail_id = avails_df['id'].tolist()[0]

                            start_list = avails_df['time_start'].tolist()
                            start_list.append(start)
                            end_list = avails_df['time_end'].tolist()
                            end_list.append(end)
                            range_new = UDatetime.remove_overlap(start_list[0], end_list[0], start_list[1], end_list[1])
                            if len(range_new) == 1:
                                start_new = range_new[0][0]
                                end_new = range_new[0][1]
                                if start_new == end_new:
                                    WorkScheduleReviseDAO.remove_available_by_id(avail_id)
                                    # WorkerAvailable.objects.filter(id__in=avail_id).delete()
                                else:
                                    date = UDatetime.pick_date_by_two_date(start_new, end_new)

                                    duration_new = end_new - start_new

                                    WorkScheduleReviseDAO.update_or_create_available(request.user,
                                                                                     start_new,
                                                                                     end_new,
                                                                                     date,
                                                                                     duration_new,
                                                                                     WorkAvailSheet.DEDUCTION,
                                                                                     worker,
                                                                                     avail_id=avail_id,
                                                                                     source='manual')
                                    # WorkerAvailable.objects.update_or_create(id__in=ids,
                                    #                                          defaults={
                                    #                                              'name': worker,
                                    #                                              'date': date,
                                    #                                              'duration': duration_new,
                                    #                                              'deduction': WorkAvailSheet.DEDUCTION,
                                    #                                              'time_start': start_new,
                                    #                                              'time_end': end_new
                                    #                                          })
                            else:
                                response = {}

                elif command_type in ['Lunch', 'Breaks', 'UnionBus']:
                    if command_type == 'Lunch':
                        # task = WorkScheduleReviseDAO.create_or_update_timeoff_lunch_task(request.user, source='manual')
                        task = Tasks.objects.get(work_order__exact='TLUNCH')
                    elif command_type == 'Breaks':
                        # task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
                        task = Tasks.objects.get(work_order__exact='TBREAK')
                    elif command_type == 'UnionBus':
                        task = WorkScheduleReviseDAO.create_or_update_union_bus_task(request.user, duration, source='manual')
                    else:
                        return JsonResponse(response)

                    available_ids = WorkerAvailable.objects.filter(time_start__lte=start,
                                                                  time_end__gte=end,
                                                                  name__exact=worker)
                    if available_ids.count() > 0:
                        available_id = available_ids[0]
                        WorkScheduleReviseDAO.update_or_create_schedule(request.user, start, end, date, duration,
                                                                        available_id, worker, task,
                                                                        source='manual')
                        # worker_scheduled = WorkerScheduled.objects.update_or_create(name=worker,
                        #                                                             date=date,
                        #                                                             time_start=start,
                        #                                                             time_end=end,
                        #                                                             task_id=task,
                        #                                                             available_id=available_id,
                        #                                                             defaults={'duration': duration})

                return JsonResponse(response)

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
                    WorkScheduleReviseDAO.remove_schedule_by_id(workerscheduledId)

                response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def add_worker_submit(request, *args, **kwargs):
                worker = request.GET.get('Worker')
                if worker:
                    worker = [worker]
                if not worker:
                    worker = request.GET.getlist('Worker[]')

                if worker:
                    worker_df = pd.DataFrame(columns=['id', 'title'])
                    worker_df['id'] = worker
                    worker_df['Avail'] = 0
                    for index, row in worker_df.iterrows():
                        name = Workers.objects.get(id=row['id']).name
                        worker_df.set_value(index, 'title', name)
                    response = worker_df.to_dict(orient='records')
                else:
                    response = []

                return JsonResponse(response, safe=False)

            @staticmethod
            def add_worker_workers(request, *args, **kwargs):

                start = request.GET.get('start')
                end = request.GET.get('end')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(days=1))

                start_date = UDatetime.pick_date_by_one_date(start)
                end_date = UDatetime.pick_date_by_one_date(end)

                workers_df = WorkScheduleDataDAO.get_all_exclude_workers_by_date_range(start_date, end_date)

                workers_df_contractor = pd.DataFrame(columns=['id', 'text'])
                workers_df_contractor['id'] = workers_df[workers_df['type'] == 'contractor']['id']
                workers_df_contractor['text'] = workers_df[workers_df['type'] == 'contractor']['name']
                if not workers_df_contractor.empty:
                    workers_dict_contractor = workers_df_contractor.to_dict(orient='records')
                else:
                    workers_dict_contractor = []

                workers_df_employee = pd.DataFrame(columns=['id', 'text'])
                workers_df_employee['id'] = workers_df[workers_df['type'] == 'employee']['id']
                workers_df_employee['text'] = workers_df[workers_df['type'] == 'employee']['name']
                if not workers_df_employee.empty:
                    workers_dict_employee = workers_df_employee.to_dict(orient='records')
                else:
                    workers_dict_employee = []

                response = [
                              {
                                  'text': 'Contractor',
                                  'children': workers_dict_contractor
                              },
                              {
                                  'text': 'Employee',
                                  'children': workers_dict_employee
                              },
                           ]

                return JsonResponse(response, safe=False)

            @staticmethod
            def worker_submit(request, *args, **kwargs):

                command_type = request.GET.get('CommandType')
                start = request.GET.get('start')
                end = request.GET.get('end')
                worker_id = request.GET.get('resourceId')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(hours=2))

                start_date = UDatetime.pick_date_by_one_date(start)
                end_date = UDatetime.pick_date_by_one_date(end)

                worker = Workers.objects.get(id=worker_id)

                response = []

                if command_type == 'ClearTasks':
                    WorkScheduleReviseDAO.remove_schedule_by_date_range_and_worker(start_date, end_date, worker)
                elif command_type == 'ClearAll':
                    WorkScheduleReviseDAO.remove_available_by_date_range_and_worker(start_date, end_date, worker)
                    WorkScheduleReviseDAO.remove_schedule_by_date_range_and_worker(start_date, end_date, worker)

                return JsonResponse(response, safe=False)

        class TableManager:
            @staticmethod
            def create(request, *args, **kwargs):
                page_size = int(request.GET.get('limit'))
                offset = int(request.GET.get('offset'))
                filters = request.GET.get('filter')
                sort = request.GET.get('sort')
                order = request.GET.get('order')

                response = WorkSchedulerPanel2Table1Manager.set_data(pagination=True,
                                                                     page_size=page_size,
                                                                     offset=offset,
                                                                     filters=filters,
                                                                     sort=sort,
                                                                     order=order
                                                                     )
                # print(response)
                data = response[0]
                num = response[1]

                if not data.empty:
                    data_response = data.to_dict(orient='records')
                    response = {
                        'total': num,
                        'rows': data_response
                    }
                else:
                    response = {
                        'total': 0,
                        'rows': []
                    }
                return JsonResponse(response, safe=False)

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
                print(start_date, end_date)

                worker_avail = WorkerAvailable.objects.filter(date__range=[start_date, end_date])
                worker_scheduled = WorkerScheduled.objects.filter(date__range=[start_date, end_date])\
                                                          .exclude(task_id__priority__in=['0', 'T'])
                worker_scheduled_others = WorkerScheduled.objects.filter(date__range=[start_date, end_date],
                                                                         task_id__priority__in=['0', 'T'])

                tasks = WorkScheduleDataDAO.get_all_tasks_open()[0]

                if worker_avail.exists():
                    worker_avail_df = pd.DataFrame.from_records(worker_avail.values('duration', 'deduction'))

                    avail = (worker_avail_df['duration']).sum().total_seconds() / 3600
                else:
                    avail = 0
                if worker_scheduled.exists():
                    worker_scheduled_df = pd.DataFrame.from_records(worker_scheduled.values('duration'))
                    scheduled = worker_scheduled_df['duration'].sum().total_seconds() / 3600
                else:
                    scheduled = 0
                if worker_scheduled_others.exists():
                    worker_scheduled_others_df = pd.DataFrame.from_records(worker_scheduled_others.values('duration'))
                    scheduled_others = worker_scheduled_others_df['duration'].sum().total_seconds() / 3600
                else:
                    scheduled_others = 0
                if not tasks.empty:
                    tasks_df = tasks[['estimate_hour', 'schedule_hour']]
                    tasks_est = tasks_df['estimate_hour'].sum()
                    tasks_count = len(tasks_df)
                    tasks_scheduled_count = len(tasks_df[tasks_df['schedule_hour'] > 0])
                else:
                    tasks_est = 0
                    tasks_count = 0
                    tasks_scheduled_count = 0
                avail_orig = avail - scheduled_others
                avail_remain = avail - scheduled - scheduled_others
                task_est_remain = tasks_est - scheduled

                response = {
                            'scheduled': scheduled,
                            'avail': avail_orig,
                            'avail_remain': avail_remain,
                            'tasks_est': tasks_est,
                            'task_est_remain': task_est_remain,
                            'tasks_count': tasks_count,
                            'tasks_scheduled_count': tasks_scheduled_count
                }

                return JsonResponse(response)

        class FormManager:

            @staticmethod
            def submit(request, *args, **kwargs):
                start = request.GET.get('Start')
                end = request.GET.get('End')

                start = UDatetime.datetime_str_init(start)
                end = UDatetime.datetime_str_init(end, start, timedelta(days=1))

                SmartScheduler(request, start, end).run()

                return JsonResponse({})
