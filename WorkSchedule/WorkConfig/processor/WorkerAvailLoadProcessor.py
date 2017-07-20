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

from configuration.WorkScheduleConstants import WorkAvailSheet
from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class WorkerAvailLoadProcessor:
    @classmethod
    def worker_avail_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='WorkerAvail')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
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

        result['worker'] = result['worker'].str.replace(', ', ',')
        result['worker'] = result['worker'].str.split(',').apply(lambda x: '{0} {1}'.format(x[1], x[0]))

        for index, row in result.iterrows():
            date = row['date']
            deduction = timedelta(hours=1)
            worker = Workers.objects.get(name=row['worker'])

            parsed_time = cls.time_parser(row['time'], row['worker'], date, shift)

            # update db
            WorkerAvailable.objects.update_or_create(name=worker,
                                                     date=date,
                                                     defaults={
                                                         'duration': parsed_time['duration'],
                                                         'time_start': parsed_time['start_datetime'],
                                                         'time_end': parsed_time['end_datetime'],
                                                         'deduction': deduction,
                                                         'source': 'file',
                                                         'document': file
                                                     })

    @classmethod
    def time_parser(cls, time_str, worker, date, shift):

        worker = Workers.objects.get(name=worker)
        if time_str in [' ', None, np.nan]:
            if shift == 'shift1' and worker.level == 'lead':

                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_LEADER.hour,
                                                 WorkAvailSheet.Shift1.DEFAULT_TIME_START_LEADER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_LEADER.hour,
                                               WorkAvailSheet.Shift1.DEFAULT_TIME_END_LEADER.minute))
                start_datetime += timedelta(days=-1)
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
                duration = WorkAvailSheet.Shift2.DEFAULT_DURATION_LEADER
            elif shift == 'shift2' and worker.level == 'worker':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_WORKER.hour,
                                                 WorkAvailSheet.Shift2.DEFAULT_TIME_START_WORKER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_WORKER.hour,
                                               WorkAvailSheet.Shift2.DEFAULT_TIME_END_WORKER.minute))
                duration = WorkAvailSheet.Shift2.DEFAULT_DURATION_WORKER
            elif shift == 'shift3' and worker.level == 'lead':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_LEADER.hour,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_LEADER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_LEADER.hour,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_LEADER.minute))
                end_datetime += timedelta(days=1)
                duration = WorkAvailSheet.Shift3.DEFAULT_DURATION_LEADER
            elif shift == 'shift3' and worker.level == 'worker':
                start_datetime = EST.localize(dt(date.year, date.month, date.day,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_WORKER.hour,
                                                 WorkAvailSheet.Shift3.DEFAULT_TIME_START_WORKER.minute))
                end_datetime = EST.localize(dt(date.year, date.month, date.day,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_WORKER.hour,
                                               WorkAvailSheet.Shift3.DEFAULT_TIME_END_WORKER.minute))
                end_datetime += timedelta(days=1)
                duration = WorkAvailSheet.Shift3.DEFAULT_DURATION_WORKER
            else:
                return None

        else:
            regex = re.compile(r'((?P<start_hour>\d{1,2})?\w{0,2}):?((?P<start_min>\d{1,2})?\w{0,2})'
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

            if shift == 'shift1':
                if start_hour < 12:
                    start_hour += 12
                    start_datetime += timedelta(days=-1, hours=12)
                else:
                    start_datetime += timedelta(hours=-12)
            elif shift == 'shift2':
                if 0 <= start_hour <= 6:
                    start_hour += 12
                    start_datetime += timedelta(hours=12)
                if 0 <= end_hour <= 6:
                    end_hour += 12
                    end_datetime += timedelta(hours=12)
            elif shift == 'shift3':
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

    @staticmethod
    def str_to_int(string):
        if string:
            string = int(string)
        else:
            string = 0
        return string