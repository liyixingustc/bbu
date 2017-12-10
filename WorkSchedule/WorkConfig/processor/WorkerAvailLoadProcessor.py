import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from accounts.models import User
from ...WorkConfig.models.models import *
from ...WorkWorkers.models.models import *
from ...WorkTasks.models.models import *

from DAO.WorkScheduleReviseDAO import WorkScheduleReviseDAO

from configuration.WorkScheduleConstants import WorkAvailSheet
from utils.UDatetime import UDatetime

from WorkSchedule.WorkConfig.tasks import *

EST = pytz.timezone(TIME_ZONE)


class WorkerAvailLoadProcessor:

    default_tasks = []
    result_path = os.path.join(BASE_DIR, 'WorkSchedule/WorkConfig/processor/result/result.csv')
    percent = 0
    file_num = 0

    @classmethod
    def worker_avail_load_processor(cls, usr_id):
        user = User.objects.get(id=usr_id)
        files = Documents.objects.filter(status__exact='new', file_type__exact='WorkerAvail')
        cls.file_num = files.count()
        cls.percent = 0

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
                    cls.worker_avail_shift_processor(user, shift3, 'shift3', file)
                    cls.percent += 0.1/cls.file_num
                    cls.update_process(cls.percent)

                    shift1 = data[worker_range_df['part'] == 2]
                    cls.worker_avail_shift_processor(user, shift1, 'shift1', file)
                    cls.percent += 0.1 / cls.file_num
                    cls.update_process(cls.percent)

                    shift2 = data[worker_range_df['part'] == 5]
                    cls.worker_avail_shift_processor(user, shift2, 'shift2', file)
                    cls.percent += 0.1 / cls.file_num
                    cls.update_process(cls.percent)

                    print(file.name)
                    intern1 = data[worker_range_df['part'] == 3].iloc[[0]]
                    intern2 = data[worker_range_df['part'] == 3].iloc[[1]]
                    intern3 = data[worker_range_df['part'] == 3].iloc[[2]]
                    intern4 = data[worker_range_df['part'] == 3].iloc[[3]]

                    cls.worker_avail_shift_processor(user, intern1, 'shift2', file, 'intern1')
                    cls.worker_avail_shift_processor(user, intern2, 'shift3', file, 'intern2')
                    cls.worker_avail_shift_processor(user, intern3, 'shift1', file, 'intern3')
                    cls.worker_avail_shift_processor(user, intern4, 'shift1', file, 'intern4')
                    cls.percent += 0.1 / cls.file_num
                    cls.update_process(cls.percent)

                    cls.add_default_tasks(cls.default_tasks)
                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                else:
                    pass

        cls.percent = 1
        cls.update_process(cls.percent)

        return JsonResponse({})

    @classmethod
    def worker_avail_shift_processor(cls, user, data, shift, file, worker_type=None):

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

            worker = Workers.objects.filter(name=row['worker'])
            if worker.exists():
                worker = worker[0]
            else:
                continue

            parsed_time = cls.time_parser(row['time'], row['worker'], date, shift, worker_type)
            if not parsed_time:
                continue

            start = parsed_time['start_datetime']
            end = parsed_time['end_datetime']
            duration = parsed_time['duration']

            # if parsed_time:
                # update db
            available = WorkScheduleReviseDAO.update_or_create_available(user,
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
            default_task = {
                            'user': user,
                            'worker': worker,
                            'date': date,
                            'start': start,
                            'end': end,
                            'duration': duration,
                            'file': file,
                            'available': available,
                            'is_union_bus': is_union_bus
                            }

            cls.default_tasks.append(default_task.copy())
            # cls.add_default_task(request, worker, date, start, end, duration, file, available,
            #                       is_union_bus)

            # else:
            #     return False
        return True

    @classmethod
    def add_default_tasks(cls, data):

        count = len(data)
        i = 0

        start_percent = cls.percent

        if data:
            for task in data:
                WorkerAvailLoadProcessor.add_default_task(
                    task['user'],
                    task['worker'],
                    task['date'],
                    task['start'],
                    task['end'],
                    task['duration'],
                    task['file'],
                    task['available'],
                    task['is_union_bus'],
                )

                i += 1
                cls.percent += 0.6/(cls.file_num*count)

                if i == 20:
                    cls.update_process(cls.percent)
                    i = 0

        cls.percent = start_percent + 0.6/cls.file_num
        cls.update_process(cls.percent)

        return

    @classmethod
    def add_default_task(cls, user, worker, date, start, end, duration, file, available_id, is_union_bus):

        # user = User.objects.get(id=user)
        # worker = Workers.objects.get(id=worker)
        # file = Documents.objects.get(id=file)
        # available_id = WorkerAvailable.objects.get(id=available_id)
        # duration = timedelta(seconds=duration)

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
            # lunch_task = WorkScheduleReviseDAO.create_or_update_timeoff_lunch_task(user, source='manual')
            lunch_task = Tasks.objects.get(work_order__exact='TLUNCH')
            lunch_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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
            # break1_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(user, source='manual')
            # break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(user, source='manual')
            break1_task = Tasks.objects.get(work_order__exact='TBREAK')
            break2_task = Tasks.objects.get(work_order__exact='TBREAK')
            break1_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
                                                                              break1_start,
                                                                              break1_end,
                                                                              date,
                                                                              break1_duration,
                                                                              available_id,
                                                                              worker,
                                                                              break1_task,
                                                                              source='file',
                                                                              document=file)
            break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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
                # break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(user, source='manual')
                break2_task = Tasks.objects.get(work_order__exact='TBREAK')
                break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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
                # break1_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(user, source='manual')
                break1_task = Tasks.objects.get(work_order__exact='TBREAK')
                break1_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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
                # break2_task = WorkScheduleReviseDAO.create_or_update_timeoff_breaks_task(user, source='manual')
                break2_task = Tasks.objects.get(work_order__exact='TBREAK')
                break2_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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

                union_bus_task = WorkScheduleReviseDAO.create_or_update_union_bus_task(user, duration,
                                                                                       source='file', document=file)
                union_bus_schedule = WorkScheduleReviseDAO.update_or_create_schedule(user,
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
    def time_parser(cls, time_str, worker, date, shift, worker_type=None):

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
                               r'((?P<start_hour>\d{1,2})?\s*(?P<start_para1>\w{0,2})?):?'
                               r'((?P<start_min>\d{1,2})?\w{0,2}\s*(?P<start_para2>\w{0,2})?)'
                               r'\s*-\s*'
                               r'((?P<end_hour>\d{1,2})?\s*(?P<end_para1>\w{0,2})?):?'
                               r'((?P<end_min>\d{1,2})?\s*(?P<end_para2>\w{0,2})?).*')
            parts = regex.match(time_str)
            if parts:
                parts = parts.groupdict()
            else:
                return None

            # parse time parameter
            AM = ['a', 'A', 'am', 'Am', 'AM']
            PM = ['p', 'P', 'pm', 'Pm', 'PM']

            if parts['start_para1'] in AM or parts['start_para2'] in AM:
                start_para = 'AM'
            elif parts['start_para1'] in PM or parts['start_para2'] in PM:
                start_para = 'PM'
            else:
                start_para = None

            if parts['end_para1'] in AM or parts['end_para2'] in AM:
                end_para = 'AM'
            elif parts['end_para1'] in PM or parts['end_para2'] in PM:
                end_para = 'PM'
            else:
                end_para = None

            # init start timestamp and end timestamp
            start_hour, start_min = cls.str_to_int(parts['start_hour']), cls.str_to_int(parts['start_min'])
            end_hour, end_min = cls.str_to_int(parts['end_hour']), cls.str_to_int(parts['end_min'])

            if start_para:
                if start_para in AM and start_hour >= 12:
                    start_hour -= 12
                elif start_para in PM and start_hour <= 12:
                    start_hour += 12

            if end_para:
                if end_para in AM and end_hour >= 12:
                    end_hour -= 12
                elif end_para in PM and end_hour <= 12:
                    end_hour += 12

            start_datetime = EST.localize(dt(date.year, date.month, date.day, start_hour, start_min))
            end_datetime = EST.localize(dt(date.year, date.month, date.day, end_hour, end_min))
            duration = end_datetime - start_datetime

            if duration <= timedelta(hours=4) or duration >= timedelta(hours=12):

                start_datetime1 = start_datetime - timedelta(days=-1)
                duration1 = end_datetime - start_datetime1
                if timedelta(hours=4) <= duration1 <= timedelta(hours=12):
                    return {
                        'start_datetime': start_datetime1,
                        'end_datetime': end_datetime,
                        'duration': duration1
                    }

                end_datetime2 = end_datetime + timedelta(days=+1)
                duration2 = end_datetime2 - start_datetime
                if timedelta(hours=4) <= duration2 <= timedelta(hours=12):
                    return {
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime2,
                        'duration': duration2
                    }
            else:
                return {
                    'start_datetime': start_datetime,
                    'end_datetime': end_datetime,
                    'duration': duration
                }

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

        if timedelta(hours=4) <= duration <= timedelta(hours=12):
            return {
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'duration': duration
            }
        else:
            return None

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

    @classmethod
    def update_process(cls, percent):
        if percent:
            percent = round(float(percent), 2)
        if os.path.exists(cls.result_path):
            data = pd.read_csv(cls.result_path)
            data_bytype = data[data['filetype'] == 'WorkerAvail']
            if data_bytype.empty:
                data_series = pd.Series({'filetype': 'WorkerAvail', 'result': percent})
                data = data.append(data_series, ignore_index=True)
            else:
                data.loc[data['filetype'] == 'WorkerAvail', ['result']] = percent
        else:
            data = pd.DataFrame({'filetype': 'WorkerAvail', 'result': percent},
                                index=[0], columns=['filetype', 'result'])

        data.to_csv(cls.result_path, index=False)

        return True
