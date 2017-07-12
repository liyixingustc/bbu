import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *

from configuration.WorkScheduleConstants import WorkAvailSheet
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class FormManager:

            media_input_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/input.xlsx')

            @classmethod
            def submit(cls, request, *args, **kwargs):
                file_type = request.GET.get('FileType')
                as_of_date = request.GET.get('AsOfDate')

                if file_type == 'Tasks':
                    cls.tasks_load(as_of_date)
                elif file_type == 'WorkerAvail':
                    cls.worker_avail_processor()

                return JsonResponse({})

            @classmethod
            def tasks_load(cls, as_of_date):

                files = Documents.objects.filter(status__exact='new', file_type__exact='Tasks')
                if files.exists():
                    for file in files:
                        path = BASE_DIR + file.document.url
                        if os.path.exists(path):
                            data = pd.read_excel(path)

                            tasks_obj = Tasks.objects.filter(current_status__in=['new', 'pending']).values()
                            tasks = pd.DataFrame.from_records(tasks_obj)

                            # data init
                            # common tasks
                            if data.empty:
                                new_tasks_list = []
                            else:
                                new_tasks_list = data['Work Order'].tolist()
                            if tasks.empty:
                                archived_tasks_list = []
                            else:
                                archived_tasks_list = tasks['work_order'].tolist()
                            common_list = list(set(new_tasks_list) & set(archived_tasks_list))

                            # update archived tasks to complete
                            if common_list:
                                tasks_update_to_complete = tasks[tasks['work_order'].isin(common_list)]
                                for index, row in tasks_update_to_complete:
                                    if row['actual_hour'] == 0:
                                        row['actual_hour'] = row['schedule_hour']
                                    Tasks.objects.filter(work_order=row['work_type']).update(current_status='completed',
                                                                                             actual_hour=row['actual_hour'])

                            # add new tasks
                            tasks_new_to_add = data[~data['Work Order'].isin(common_list)]
                            tasks_new_to_add['Priority'] = tasks_new_to_add['Priority'].apply(lambda x:
                                                                                              str(x).upper()if x
                                                                                              else None
                                                                                              )
                            tasks_new_to_add['Date Kitted'] = tasks_new_to_add['Date Kitted'].apply(lambda x:
                                                                                                    EST.localize(x) if x
                                                                                                    else UDatetime.now_local)
                            tasks_new_to_add['line'] = tasks_new_to_add['Date Kitted'].apply(lambda x:
                                                                                                    x if x else '1')

                            if not tasks_new_to_add.empty:
                                for index, row in tasks_new_to_add.iterrows():
                                    Tasks.objects.update_or_create(work_order=row['Work Order'],
                                                                   defaults={'line': '1',
                                                                             'equipment': row['Charge To Name'],
                                                                             'description': row['Description'],
                                                                             'work_type': 'CM',
                                                                             'priority': row['Priority'],
                                                                             'create_on': row['Date Kitted'],
                                                                             'requested_by': row['Requested by'],
                                                                             'estimate_hour': timedelta(hours=int(row['Man Hrs'])),
                                                                             'current_status': 'new'
                                                                             })

                            # update documents
                            Documents.objects.filter(id=file.id).update(status='loaded')

                            return JsonResponse({})
                else:
                    return JsonResponse({})


            @classmethod
            def worker_avail_processor(cls):

                files = Documents.objects.filter(status__exact='new',file_type__exact='WorkerAvail')
                if files.exists():
                    for file in files:
                        path = BASE_DIR+file.document.url
                        if os.path.exists(path):
                            data = pd.read_excel(path, header=0, skiprows=[0, 1, 2, 4], skip_footer=4, parse_cols='A:H')
                            data.rename(columns={data.columns[0]: "worker"}, inplace=True)

                            # data init
                            shift1 = data.iloc[0:11]
                            cls.worker_avail_shift_processor(shift1, 'shift1', file)

                            shift2 = data.iloc[12:23]
                            cls.worker_avail_shift_processor(shift2, 'shift2', file)

                            shift3 = data.iloc[35:46]
                            cls.worker_avail_shift_processor(shift3, 'shift3', file)

                            # update documents
                            Documents.objects.filter(id=file.id).update(status='loaded')

                        else:
                            pass

                return JsonResponse({})

            @classmethod
            def worker_avail_shift_processor(cls, data, shift, file):

                data = data.dropna(how='all')
                data_melt = pd.melt(data, id_vars=["worker"],
                                    var_name="date", value_name="time")

                result = data_melt[~data_melt['time'].isin(WorkAvailSheet.TIME_OFF)]
                result = result.assign(duration=timedelta(hours=0))

                if shift == 'shift1':
                    for index, row in result.iterrows():
                        date = row['date']
                        deduction = timedelta(hours=1)

                        # init time
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                             WorkAvailSheet.Shift1.DEFAULT_TIME_START.hour,
                                                             WorkAvailSheet.Shift1.DEFAULT_TIME_START.minute))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                           WorkAvailSheet.Shift1.DEFAULT_TIME_END.hour,
                                                           WorkAvailSheet.Shift1.DEFAULT_TIME_END.minute))
                            start_datetime += timedelta(days=-1)
                            duration = timedelta(hours=9)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time'])
                            if parts:
                                parts = parts.groupdict()
                            else:
                                continue

                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = EST.localize(dt(date.year, date.month, date.day, start_hour, start_min))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day, end_hour, end_min))
                            if start_hour < 12:
                                start_hour += 12
                                start_datetime += timedelta(days=-1, hours=12)
                            else:
                                start_datetime += timedelta(hours=-12)

                            duration = end_datetime - start_datetime

                        # update db
                        worker = Workers.objects.get_or_create(name=row['worker'])[0]
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'duration': duration,
                                                                     'time_start': start_datetime,
                                                                     'time_end': end_datetime,
                                                                     'deduction': deduction,
                                                                     'source': 'file',
                                                                     'document': file
                                                                 })
                elif shift == 'shift2':
                    for index, row in result.iterrows():
                        date = row['date']
                        deduction = timedelta(hours=1)

                        # init time
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                             WorkAvailSheet.Shift2.DEFAULT_TIME_START.hour,
                                                             WorkAvailSheet.Shift2.DEFAULT_TIME_START.minute))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                           WorkAvailSheet.Shift2.DEFAULT_TIME_END.hour,
                                                           WorkAvailSheet.Shift2.DEFAULT_TIME_END.minute))
                            duration = timedelta(hours=9)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time'])
                            if parts:
                                parts = parts.groupdict()
                            else:
                                continue

                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = EST.localize(dt(date.year, date.month, date.day, start_hour, start_min))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day, end_hour, end_min))
                            if 0 <= start_hour <= 6:
                                start_hour += 12
                                start_datetime += timedelta(hours=12)
                            if 0 <= end_hour <= 6:
                                end_hour += 12
                                end_datetime += timedelta(hours=12)

                            duration = end_datetime - start_datetime

                        # update db
                        worker = Workers.objects.get_or_create(name=row['worker'])[0]
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'duration': duration,
                                                                     'time_start': start_datetime,
                                                                     'time_end': end_datetime,
                                                                     'deduction': deduction,
                                                                     'source': 'file',
                                                                     'document': file
                                                                 })
                elif shift == 'shift3':
                    for index, row in result.iterrows():
                        date = row['date']
                        deduction = timedelta(hours=1)

                        # init time
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                             WorkAvailSheet.Shift3.DEFAULT_TIME_START.hour,
                                                             WorkAvailSheet.Shift3.DEFAULT_TIME_START.minute))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                           WorkAvailSheet.Shift3.DEFAULT_TIME_END.hour,
                                                           WorkAvailSheet.Shift3.DEFAULT_TIME_END.minute))
                            end_datetime += timedelta(days=1)
                            duration = timedelta(hours=9)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time'])
                            if parts:
                                parts = parts.groupdict()
                            else:
                                continue

                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = EST.localize(dt(date.year, date.month, date.day, start_hour, start_min))
                            end_datetime = EST.localize(dt(date.year, date.month, date.day, end_hour, end_min))
                            if 0 <= end_hour < 6:
                                end_datetime += timedelta(days=1)
                            elif 6 <= end_hour <= 12:
                                end_hour += 12
                                end_datetime += timedelta(hours=12)
                            start_datetime += timedelta(hours=12)

                            duration = end_datetime - start_datetime - timedelta(hours=1)

                        # update db
                        worker = Workers.objects.get_or_create(name=row['worker'])[0]
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'duration': duration,
                                                                     'time_start': start_datetime,
                                                                     'time_end': end_datetime,
                                                                     'deduction': deduction,
                                                                     'source': 'file',
                                                                     'document': file
                                                                 })

            @staticmethod
            def str_to_int(string):
                if string:
                    string = int(string)
                else:
                    string = 0
                return string

            @classmethod
            def fileupload(cls,request, *args, **kwargs):
                if request.method == 'POST' and request.FILES.get('FileUpload'):
                    file = request.FILES.get('FileUpload')
                    FileType = request.POST.get('FileType')
                    Processor = request.POST.get('Processor')

                    try:
                        document = Documents.objects.get(name__exact=file.name)
                        document.document.delete(False)
                    except Exception as e:
                        pass

                    Documents.objects.update_or_create(name=file.name,
                                                       defaults={'document': file,
                                                                 'status': 'new',
                                                                 'file_type': FileType,
                                                                 'processor': Processor,
                                                                 'created_by': request.user})

                return JsonResponse({})