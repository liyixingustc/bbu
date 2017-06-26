import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz

from bbu.settings import TIME_ZONE
from django.http import JsonResponse

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *

from configuration.WorkScheduleConstants import WorkAvailSheet

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
                    cls.worker_avail_load()

                return JsonResponse({})

            @classmethod
            def tasks_load(cls, as_of_date):

                if os.path.exists(cls.media_input_filepath):
                    data = pd.read_excel(cls.media_input_filepath)
                else:
                    return JsonResponse({})

                tasks_obj = Tasks.objects.filter(current_status__in=['new', 'pending']).values()
                tasks = pd.DataFrame.from_records(tasks_obj)

                # data init
                # common tasks
                new_tasks_list = data['Work Order'].tolist()
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
                if not tasks_new_to_add.empty:
                    for index, row in tasks_new_to_add.iterrows():
                        Tasks.objects.update_or_create(work_order=row['Work Order'],
                                                       defaults={'line': '1',
                                                                 'equipment': row['Charge To Name'],
                                                                 'description': row['Description'],
                                                                 'work_type': 'CM',
                                                                 'priority': '1',
                                                                 'create_on': row['Date Kitted'],
                                                                 'requested_by': row['Requested by'],
                                                                 'estimate_hour': timedelta(hours=int(row['Man Hrs'])),
                                                                 'current_status': 'new'
                                                                 })

                return JsonResponse({})

            @classmethod
            def worker_avail_load(cls):

                if os.path.exists(cls.media_input_filepath):
                    data = pd.read_excel(cls.media_input_filepath, header=0, skiprows=[0, 1, 2, 4], skip_footer=5,
                                         parse_cols='A:H')
                    data.rename(columns={data.columns[0]: "worker"}, inplace=True)

                    # data init
                    shift1 = data.iloc[0:11]
                    cls.worker_avail_processor(shift1, 'shift1')

                    shift2 = data.iloc[12:23]
                    cls.worker_avail_processor(shift2, 'shift2')

                    shift3 = data.iloc[-11:]
                    cls.worker_avail_processor(shift3, 'shift3')

                    return JsonResponse({})
                else:
                    return JsonResponse({})

            @classmethod
            def worker_avail_processor(cls, data, shift):

                data = data.dropna(how='all')
                data_melt = pd.melt(data, id_vars=["worker"],
                                    var_name="date", value_name="time")

                result = data_melt[~data_melt['time'].isin(WorkAvailSheet.TIME_OFF)]
                result['duration'] = timedelta(hours=0)

                if shift == 'shift1':
                    for index, row in result.iterrows():
                        date = row['date']
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = dt(date.year, date.month, date.day,
                                                WorkAvailSheet.Shift1.DEFAULT_TIME_START.hour,
                                                WorkAvailSheet.Shift1.DEFAULT_TIME_START.minute,
                                                tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day,
                                              WorkAvailSheet.Shift1.DEFAULT_TIME_END.hour,
                                              WorkAvailSheet.Shift1.DEFAULT_TIME_END.minute,
                                              tzinfo=EST)
                            start_datetime += timedelta(days=-1)
                            duration = timedelta(hours=8)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time']).groupdict()
                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = dt(date.year, date.month, date.day, start_hour, start_min, tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day, end_hour, end_min, tzinfo=EST)
                            if start_hour < 12:
                                start_hour += 12
                                start_datetime += timedelta(days=-1, hours=12)
                            else:
                                start_datetime += timedelta(hours=-12)

                            duration = end_datetime - start_datetime - timedelta(hours=1)

                        # update db
                        worker = Workers.objects.get_or_create(name=row['worker'])[0]
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'duration': duration,
                                                                     'time_start': start_datetime,
                                                                     'time_end': end_datetime
                                                                 })
                elif shift == 'shift2':
                    for index, row in result.iterrows():
                        date = row['date']
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = dt(date.year, date.month, date.day,
                                                WorkAvailSheet.Shift2.DEFAULT_TIME_START.hour,
                                                WorkAvailSheet.Shift2.DEFAULT_TIME_START.minute,
                                                tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day,
                                              WorkAvailSheet.Shift2.DEFAULT_TIME_END.hour,
                                              WorkAvailSheet.Shift2.DEFAULT_TIME_END.minute,
                                              tzinfo=EST)
                            duration = timedelta(hours=8)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time']).groupdict()
                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = dt(date.year, date.month, date.day, start_hour, start_min, tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day, end_hour, end_min, tzinfo=EST)
                            if 0 <= start_hour <= 6:
                                start_hour += 12
                                start_datetime += timedelta(hours=12)
                            if 0 <= end_hour <= 6:
                                end_hour += 12
                                end_datetime += timedelta(hours=12)

                            duration = end_datetime - start_datetime - timedelta(hours=1)

                        # update db
                        worker = Workers.objects.get_or_create(name=row['worker'])[0]
                        WorkerAvailable.objects.update_or_create(name=worker,
                                                                 date=date,
                                                                 defaults={
                                                                     'duration': duration,
                                                                     'time_start': start_datetime,
                                                                     'time_end': end_datetime
                                                                 })
                elif shift == 'shift3':
                    for index, row in result.iterrows():
                        date = row['date']
                        if row['time'] in [' ', None, np.nan]:
                            start_datetime = dt(date.year, date.month, date.day,
                                                WorkAvailSheet.Shift3.DEFAULT_TIME_START.hour,
                                                WorkAvailSheet.Shift3.DEFAULT_TIME_START.minute,
                                                tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day,
                                              WorkAvailSheet.Shift3.DEFAULT_TIME_END.hour,
                                              WorkAvailSheet.Shift3.DEFAULT_TIME_END.minute,
                                              tzinfo=EST)
                            end_datetime += timedelta(days=1)
                            duration = timedelta(hours=8)
                        else:
                            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                                               r'\s*-\s*'
                                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
                            parts = regex.match(row['time']).groupdict()
                            start_hour, start_min = cls.str_to_int(parts['start_hour']), \
                                cls.str_to_int(parts['start_min'])
                            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

                            # init start timestamp and end timestamp
                            start_datetime = dt(date.year, date.month, date.day, start_hour, start_min, tzinfo=EST)
                            end_datetime = dt(date.year, date.month, date.day, end_hour, end_min, tzinfo=EST)
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
                                                                     'time_end': end_datetime
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
                file = request.FILES.get('FileUpload')
                with open(cls.media_input_filepath, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                return JsonResponse({})