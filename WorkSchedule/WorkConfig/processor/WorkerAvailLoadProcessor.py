import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from ...WorkConfig.models.models import *
from ...WorkWorkers.models.models import *
from ...WorkTasks.models.models import *

from DAO.WorkScheduleReviseDAO import WorkScheduleReviseDAO

from configuration.WorkScheduleConstants import WorkAvailSheet
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkerAvailLoadProcessor:
    @classmethod
    def worker_avail_load_processor(cls, request):

        files = Documents.objects.filter(status__exact='new', file_type__exact='WorkerAvail')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_excel(path, header=None, parse_cols='A:H')
                    data = cls.header_processor(data)
                    if data.empty:
                        break
                    data.rename(columns={data.columns[0]: "worker"}, inplace=True)

                    # find the range for each shift

                    worker_range = data['worker'].str.contains('^[a-zA-Z\'\-]+\s*,\s*[a-zA-Z\'\-]+$', regex=True, na=False)
                    worker_range_df = pd.DataFrame(worker_range)
                    worker_range_df['worker'] = worker_range_df['worker'].astype(int)
                    worker_range_df['part'] = 0

                    part = 1
                    last = 1
                    for index, row in worker_range_df.iterrows():
                        if row['worker'] == 1 and last == 1:
                            worker_range_df.set_value(index, 'part', part)
                        elif row['worker'] == 1 and last == 0:
                            part += 1
                            worker_range_df.set_value(index, 'part', part)

                        last = row['worker']

                    # data init
                    shift3 = data[worker_range_df['part'] == 1]
                    cls.worker_avail_shift_processor(request, shift3, 'shift3', file)

                    shift1 = data[worker_range_df['part'] == 2]
                    cls.worker_avail_shift_processor(request, shift1, 'shift1', file)

                    shift2 = data[worker_range_df['part'] == 5]
                    cls.worker_avail_shift_processor(request, shift2, 'shift2', file)
                    print(file.name)
                    intern1 = data[worker_range_df['part'] == 3].iloc[[0]]
                    intern2 = data[worker_range_df['part'] == 3].iloc[[1]]
                    intern3 = data[worker_range_df['part'] == 3].iloc[[2]]
                    intern4 = data[worker_range_df['part'] == 3].iloc[[3]]

                    cls.worker_avail_shift_processor(request, intern1, 'shift2', file)
                    cls.worker_avail_shift_processor(request, intern2, 'shift3', file)
                    cls.worker_avail_shift_processor(request, intern3, 'shift1', file)
                    cls.worker_avail_shift_processor(request, intern4, 'shift1', file)

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                else:
                    pass

        return JsonResponse({})

    @classmethod
    def worker_avail_shift_processor(cls, request, data, shift, file):

        data = data.dropna(how='all')
        data_melt = pd.melt(data, id_vars=["worker"],
                            var_name="date", value_name="time")

        result = data_melt[~data_melt['time'].isin(WorkAvailSheet.TIME_OFF)]
        result = result.assign(duration=timedelta(hours=0))

        # result = result[result['worker'].str.contains('^[a-zA-Z\'\-]+\s*,\s*[a-zA-Z\'\-]+$', regex=True, na=False)]

        result['worker'] = result['worker'].str.replace(', ', ',')
        result['worker'] = result['worker'].str.split(',').apply(lambda x: '{0} {1}'.format(x[1], x[0]))

        for index, row in result.iterrows():
            is_union_bus = False
            if row['time'] == 'Union Bus.':
                row['time'] = None
                is_union_bus = True
            date = row['date']
            deduction = timedelta(hours=1)
            worker = Workers.objects.get(name=row['worker'])
            parsed_time = cls.time_parser(row['time'], row['worker'], date, shift)

            start = parsed_time['start_datetime']
            end = parsed_time['end_datetime']
            duration = parsed_time['duration']

            # if parsed_time:
                # update db
            available = WorkScheduleReviseDAO.update_or_create_available(request.user,
                                                                         start,
                                                                         end,
                                                                         date,
                                                                         duration,
                                                                         WorkAvailSheet.DEDUCTION,
                                                                         worker,
                                                                         source='manual')
            # available = WorkerAvailable.objects.update_or_create(name=worker,
            #                                                      date=date,
            #                                                      defaults={
            #                                                          'duration': parsed_time['duration'],
            #                                                          'time_start': parsed_time['start_datetime'],
            #                                                          'time_end': parsed_time['end_datetime'],
            #                                                          'deduction': deduction,
            #                                                          'source': 'file',
            #                                                          'document': file
            #                                                      })

            # additional tasks
            cls.add_default_tasks(request, worker, date, start, end, duration, file, available,
                                  is_union_bus)

            # else:
            #     return False
        return True

    @classmethod
    def add_default_tasks(cls, request, worker, date, start, end, duration, file, available_id, is_union_bus):

        lunch_task = None
        lunch_schedule = None
        break1_task = None
        break1_schedule = None
        break2_task = None
        break2_schedule = None
        union_bus_task = None
        union_bus_schedule = None

        # add lunch
        lunch_obj = WorkerScheduled.objects.filter(date=date, name=worker, task_id__description='Lunch Time')
        if not lunch_obj.exists():
            lunch_start = end - timedelta(minutes=60)
            lunch_end = end - timedelta(minutes=30)
            lunch_duration = lunch_end - lunch_start
            lunch_task = WorkScheduleReviseDAO.create_or_update_timeoff_lunch_task(request.user, source='manual')
            lunch_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                             lunch_start,
                                                                             lunch_end,
                                                                             date,
                                                                             lunch_duration,
                                                                             available_id,
                                                                             worker,
                                                                             lunch_task,
                                                                             source='file',
                                                                             document=file)
        # add breaks
        break_obj = WorkerScheduled.objects.filter(date=date, name=worker, task_id__description='Break Time')
        break1_start = end - timedelta(minutes=30)
        break1_end = end - timedelta(minutes=15)
        break1_duration = break1_end - break1_start
        break2_start = end - timedelta(minutes=15)
        break2_end = end - timedelta(minutes=0)
        break2_duration = break2_end - break2_start
        if not break_obj.exists():
            break1_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
            break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
            break1_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                              break1_start,
                                                                              break1_end,
                                                                              date,
                                                                              break1_duration,
                                                                              available_id,
                                                                              worker,
                                                                              break1_task,
                                                                              source='file',
                                                                              document=file)
            break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                              break2_start,
                                                                              break2_end,
                                                                              date,
                                                                              break2_duration,
                                                                              available_id,
                                                                              worker,
                                                                              break2_task,
                                                                              source='file',
                                                                              document=file)
        if break_obj.count() == 1:
            break_obj_exist = break_obj[0]
            if break_obj_exist.time_start == break1_start and break_obj_exist.time_end == break1_end:
                break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
                break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                                  break2_start,
                                                                                  break2_end,
                                                                                  date,
                                                                                  break2_duration,
                                                                                  available_id,
                                                                                  worker,
                                                                                  break2_task,
                                                                                  source='file',
                                                                                  document=file)
            elif break_obj_exist.time_start == break2_start and break_obj_exist.time_end == break2_end:
                break1_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
                break1_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                                  break1_start,
                                                                                  break1_end,
                                                                                  date,
                                                                                  break1_duration,
                                                                                  available_id,
                                                                                  worker,
                                                                                  break1_task,
                                                                                  source='file',
                                                                                  document=file)
            else:
                break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(request.user, source='manual')
                break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                                  break2_start,
                                                                                  break2_end,
                                                                                  date,
                                                                                  break2_duration,
                                                                                  available_id,
                                                                                  worker,
                                                                                  break2_task,
                                                                                  source='file',
                                                                                  document=file)

        # add union business
        if is_union_bus:


            union_bus_obj = WorkerScheduled.objects.filter(date=date, name=worker, task_id__description='Union Business')
            if not union_bus_obj.exists():
                union_bus_start = start
                union_bus_end = end - timedelta(minutes=60)
                union_bus_duration = union_bus_end - union_bus_start

                union_bus_task = WorkScheduleReviseDAO.create_or_update_union_bus_task(request.user, duration,
                                                                                       source='file', document=file)
                union_bus_schedule = WorkScheduleReviseDAO.update_or_create_schedule(request.user,
                                                                                     union_bus_start,
                                                                                     union_bus_end,
                                                                                     date,
                                                                                     union_bus_duration,
                                                                                     available_id,
                                                                                     worker,
                                                                                     union_bus_task,
                                                                                     source='file',
                                                                                     document=file)

        return {
            'lunch_task': lunch_task,
            'lunch_schedule': lunch_schedule,
            'break1_task': break1_task,
            'break1_schedule': break1_schedule,
            'break2_task': break2_task,
            'break2_schedule': break2_schedule,
            'union_bus_task': union_bus_task,
            'union_bus_schedule': union_bus_schedule
        }

    @classmethod
    def time_parser(cls, time_str, worker, date, shift):

        worker = Workers.objects.get(name=worker)
        if time_str in [' ', None, np.nan, '/T', 'T/', 'T']:
            if shift == 'shift3' and worker.level == 'lead':

                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_LEADER.hour,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_LEADER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_LEADER.hour,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_LEADER.minute))
                start_datetime += timedelta(days=-1)
                duration = WorkAvailSheet.Shift3.DEFAULT_DURATION_LEADER
            elif shift == 'shift3' and worker.level == 'worker':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_WORKER.hour,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_WORKER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_WORKER.hour,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_WORKER.minute))
                duration = WorkAvailSheet.Shift3.DEFAULT_DURATION_WORKER
            elif shift == 'shift1' and worker.level == 'lead':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_LEADER.hour,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_LEADER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_LEADER.hour,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_LEADER.minute))
                duration = WorkAvailSheet.Shift1.DEFAULT_DURATION_LEADER
            elif shift == 'shift1' and worker.level == 'worker':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_WORKER.hour,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_WORKER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_WORKER.hour,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_WORKER.minute))
                duration = WorkAvailSheet.Shift1.DEFAULT_DURATION_WORKER
            elif shift == 'shift2' and worker.level == 'lead':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_LEADER.hour,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_LEADER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_LEADER.hour,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_LEADER.minute))
                end_datetime += timedelta(days=1)
                duration = WorkAvailSheet.Shift2.DEFAULT_DURATION_LEADER
            elif shift == 'shift2' and worker.level == 'worker':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_WORKER.hour,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_WORKER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_WORKER.hour,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_WORKER.minute))
                end_datetime += timedelta(days=1)
                duration = WorkAvailSheet.Shift2.DEFAULT_DURATION_WORKER
            else:
                return None

        else:
            regex = re.compile(r'(\s*T\s*/\s*)?'
                               r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
                               r'\s*-\s*'
                               r'((?P<end_hour>\d{1,2})?\w{0,2}):?((?P<end_min>\d{1,2})?\w{0,2}).*')
            parts = regex.match(time_str)
            if parts:
                parts = parts.groupdict()
            else:
                return None

            start_hour, start_min = cls.str_to_int(parts['start_hour']), cls.str_to_int(parts['start_min'])
            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

            # init start timestamp and end timestamp

            start_datetime = EST.localize(dt(date.year, date.month, date.day, start_hour, start_min))
            end_datetime = EST.localize(dt(date.year, date.month, date.day, end_hour, end_min))

            if shift == 'shift3':
                if start_hour < 12:
                    start_hour += 12
                    start_datetime += timedelta(days=-1, hours=12)
                else:
                    start_datetime += timedelta(hours=-12)
            elif shift == 'shift1':
                if 0 <= start_hour <= 6:
                    start_hour += 12
                    start_datetime += timedelta(hours=12)
                if 0 <= end_hour <= 6:
                    end_hour += 12
                    end_datetime += timedelta(hours=12)
            elif shift == 'shift2':
                if 0 <= end_hour < 6:
                    end_datetime += timedelta(days=1)
                elif 6 <= end_hour <= 12:
                    end_hour += 12
                    end_datetime += timedelta(hours=12)
                start_datetime += timedelta(hours=12)

            duration = end_datetime - start_datetime

        return {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'duration': duration
        }

    @classmethod
    def header_processor(cls, data):

        header_range = data[1].str.contains('^\s*SAT[\.]?\s*$', regex=True, na=False)
        header_range_len = len(header_range[header_range])
        if header_range_len == 1:
            header_index = header_range[header_range].index.tolist()[0]
            data.columns = data.iloc[header_index-1].values
            data = data[(header_index + 1):]
            data.reset_index(inplace=True, drop=True)
        else:
            data = pd.DataFrame()

        return data

    @staticmethod
    def str_to_int(string):
        if string:
            string = int(string)
        else:
            string = 0
        return string
