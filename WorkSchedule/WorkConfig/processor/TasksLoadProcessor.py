import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'bbu.settings'
django.setup()

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from WorkSchedule.WorkConfig.models.models import *
from WorkSchedule.WorkWorkers.models.models import *
from WorkSchedule.WorkTasks.models.models import *

from utils.UDatetime import UDatetime

from WorkSchedule.WorkScheduler import tasks

EST = pytz.timezone(TIME_ZONE)


class TasksLoadProcessor:

    @classmethod
    def tasks_load_processor(cls, files_path=None):

        if files_path:
            print(files_path)
            # for file_path in files_path:
            # if os.path.exists(files_path):
            data = pd.read_csv(files_path, encoding='iso-8859-1', engine='python')
            # data = pd.read_csv(file_path)
            cls.tasks_data_processor(data)
            # else:
            #     return JsonResponse({})
        else:
            files = Documents.objects.filter(status__exact='new', file_type__exact='Tasks')
            if files.exists():
                for file in files:
                    path = BASE_DIR + file.document.url
                    if os.path.exists(path):
                        data = pd.read_csv(path, encoding='iso-8859-1')
                        # data = pd.read_csv(path)
                        cls.tasks_data_processor(data)

                        # update documents
                        Documents.objects.filter(id=file.id).update(status='loaded')

                        return JsonResponse({})
            else:
                return JsonResponse({})

    @classmethod
    def tasks_data_processor(cls, data_new):

        data_old = pd.DataFrame.from_records(Tasks.objects.all().values('work_order',
                                                                        'current_status_somax'))
        data = cls.get_new_and_update_data(data_old, data_new)
        # print(len(data))
        if data.empty:
            return

        try:
            data['Created'] = pd.to_datetime(data['Created'], format='%Y/%m/%d')
        except:
            try:
                data['Created'] = pd.to_datetime(data['Created'], format='%m/%d/%Y')
            except:
                data['Created'] = pd.to_datetime(data['Created'], format='%m/%d/%y')
        data['Created'] = data['Created'].apply(lambda x: UDatetime.localize(x))

        try:
            data['Scheduled'] = pd.to_datetime(data['Scheduled'], format='%Y/%m/%d')
        except:
            data['Scheduled'] = pd.to_datetime(data['Scheduled'], format='%m/%d/%Y')
        data['Scheduled'] = data['Scheduled'].apply(lambda x: UDatetime.localize(x))

        try:
            data['Actual Finish'] = pd.to_datetime(data['Actual Finish'], format='%Y/%m/%d')
        except:
            try:
                data['Actual Finish'] = pd.to_datetime(data['Actual Finish'], format='%m/%d/%Y')
            except:
                data['Actual Finish'] = pd.to_datetime(data['Actual Finish'], format='%m/%d/%y')
        data['Actual Finish'] = data['Actual Finish'].apply(lambda x: UDatetime.localize(x))

        data['Description'] = data['Description'].apply(lambda x: x.encode('ascii', errors="ignore").decode())

        for index, row in data.iterrows():
            # if index in list(np.arange(0,40000, 100)):
            #     print(index)
            equipment = Equipment.objects.filter(equipment_id__exact=row['Charge To'])
            if equipment.exists():
                equipment = equipment[0]
            else:
                equipment = None

            aor = AOR.objects.filter(equip_id__equipment_id__exact=row['Charge To'])
            if aor.exists():
                aor = aor[0]
            else:
                aor = None

            creator = SomaxAccount.objects.filter(user_name__exact=row['Creator'])
            if creator.exists():
                creator = creator[0]
            else:
                creator = None

            assigned = SomaxAccount.objects.filter(user_name__exact=row['Assigned'])
            if assigned.exists():
                assigned = assigned[0]
            else:
                assigned = None

            pms = PMs.objects.filter(description__exact=row['Description'])
            if pms.exists():
                pms = pms[0]
                est = pms.duration
                due_days = pms.due_days
            else:
                pms = None
                est = timedelta(hours=0)
                due_days = None

            current_status = row['Status']
            # current_status = cls.smart_status_choice(row['Work Order'], row['Status'], due_days, row['Created'])

            Tasks.objects.update_or_create(work_order=row['Work Order'],
                                           defaults={
                                               'description': row['Description'],
                                               'work_type': row['Type'],
                                               'current_status': current_status,
                                               'line': None,
                                               'shift': row['Shift'],
                                               'priority': row['Priority'],
                                               'create_date': row['Created'],
                                               'current_status_somax': row['Status'],
                                               'schedule_date_somax': row['Scheduled'],
                                               'actual_date_somax': row['Actual Finish'],
                                               'estimate_hour': est,
                                               'fail_code': row['Fail Code'],
                                               'completion_comments': row['Completion Comments'],
                                               'equipment': equipment,
                                               'AOR': aor,
                                               'creator': creator,
                                               'assigned': assigned,
                                               'PMs': pms,
                                               'parts_location': None
                                           })

        # auto schedule
        # work_orders = data['Work Order'].tolist()
        # tasks.auto_schedule.delay(work_orders=work_orders)
    #
    # @classmethod
    # def filter_parts_status(cls, data):
    #
    #     data[data['description'].str.contains('{{parts open}}') & data['Status'] == 'Approved']['Status'] = 'Wait For Parts'
    #     data[data['description'].str.contains('{{parts complete}}') & data['Status'] == 'Wait For Parts']['Status'] = 'Approved'
    #
    #     return data

    @classmethod
    def get_new_and_update_data(cls, old, new):

        if new.empty:
            return pd.DataFrame()
        if old.empty:
            return new

        new['Work Order'] = new['Work Order'].astype(str)

        merged = pd.merge(new, old, how='left', left_on=['Work Order'], right_on=['work_order'])

        data = merged[(merged['Status'] != merged['current_status_somax']) |
                      (merged['work_order'].isnull())]

        return data

    close_status = ['Canceled', 'Complete', 'Denied']
    open_status = ['Approved', 'Scheduled', 'Work Request', 'Wait For Parts']

    @classmethod
    def smart_status_choice(cls, work_order, somax_status, due_days, create_date):

        task_obj = Tasks.objects.filter(work_order=work_order)
        if task_obj.exists():
            current_status = task_obj[0].current_status
            # create_date = task_obj[0].create_date
            if due_days:
                today = UDatetime.now_local()
                is_overdue = ((create_date + due_days) < today)
                if is_overdue:
                    if current_status in cls.open_status and somax_status in cls.open_status:
                        if current_status == 'Scheduled' or somax_status == 'Scheduled':
                            current_status = 'Complete'
                        else:
                            current_status = 'Canceled'
                    elif current_status in cls.close_status and somax_status in cls.open_status:
                        current_status = current_status
                    else:
                        current_status = somax_status
                else:
                    if current_status in cls.open_status and somax_status in cls.open_status:
                        if somax_status == 'Scheduled' and current_status != 'Scheduled':
                            current_status = 'Approved'
                        elif somax_status == 'Approved' and current_status == 'Work Request':
                            current_status = 'Approved'
                        else:
                            current_status = current_status
                    elif current_status in cls.close_status and somax_status in cls.open_status:
                        current_status = current_status
                    else:
                        current_status = somax_status
            else:
                if current_status in cls.open_status and somax_status in cls.open_status:
                    current_status = current_status
                elif current_status in cls.close_status and somax_status in cls.open_status:
                    current_status = current_status
                else:
                    current_status = somax_status
        else:
            current_status = somax_status
            if due_days:
                today = UDatetime.now_local()
                is_overdue = ((create_date + due_days) < today)
                if is_overdue:
                    if somax_status in ['Approved', 'Work Request']:
                        current_status = 'Canceled'
                    elif somax_status in ['Scheduled']:
                        current_status = 'Complete'
                else:
                    if somax_status == 'Scheduled':
                        current_status = 'Approved'
            else:
                if somax_status == 'Scheduled':
                    current_status = 'Approved'

        return current_status

    # @classmethod
    # def tasks_load_processor(cls):
    #
    #     files = Documents.objects.filter(status__exact='new', file_type__exact='Tasks')
    #     if files.exists():
    #         for file in files:
    #             path = BASE_DIR + file.document.url
    #             if os.path.exists(path):
    #                 data = pd.read_excel(path)
    #                 data.dropna(inplace=True, how='all')
    #
    #                 tasks_obj = Tasks.objects.filter(current_status__in=['new', 'pending']).values()
    #                 tasks = pd.DataFrame.from_records(tasks_obj)
    #
    #                 # data init
    #                 # common tasks
    #                 if data.empty:
    #                     new_tasks_list = []
    #                 else:
    #                     new_tasks_list = data['Work Order'].tolist()
    #                 if tasks.empty:
    #                     archived_tasks_list = []
    #                 else:
    #                     archived_tasks_list = tasks['work_order'].tolist()
    #                 common_list = list(set(new_tasks_list) & set(archived_tasks_list))
    #
    #                 # update archived tasks to complete
    #                 if common_list:
    #                     tasks_update_to_complete = tasks[tasks['work_order'].isin(common_list)]
    #                     for index, row in tasks_update_to_complete:
    #                         if row['actual_hour'] == 0:
    #                             row['actual_hour'] = row['schedule_hour']
    #                         Tasks.objects.filter(work_order=row['work_type']).update(current_status='completed',
    #                                                                                  actual_hour=row['actual_hour'])
    #
    #                 # add new tasks
    #                 tasks_new_to_add = data[~data['Work Order'].isin(common_list)]
    #                 tasks_new_to_add['Work Order'] = tasks_new_to_add['Work Order'].apply(lambda x: str(int(x)))
    #                 tasks_new_to_add['Priority'] = tasks_new_to_add['Priority'].apply(lambda x:
    #                                                                                   str(x).upper() if x
    #                                                                                   else None
    #                                                                                   )
    #                 # print(tasks_new_to_add)
    #                 tasks_new_to_add['Date Kitted'] = tasks_new_to_add['Date Kitted'].apply(lambda x:
    #                                                                                         UDatetime.local_tz
    #                                                                                         .localize(x)
    #                                                                                         if x
    #                                                                                         else UDatetime.now_local)
    #                 tasks_new_to_add['line'] = tasks_new_to_add['Date Kitted'].apply(lambda x:
    #                                                                                  x if x else '1')
    #
    #                 if not tasks_new_to_add.empty:
    #                     for index, row in tasks_new_to_add.iterrows():
    #
    #                         regex = re.compile(
    #                             r'.*'
    #                             r'\s+'
    #                             r'(?P<code>[A-Z][0-9a-zA-Z\_\-]+)\s*(\(.*\))*?$')
    #                         parts = regex.match(row['Charge To Name'])
    #                         aor = AOR.objects.get(equip_code__exact='NONE')
    #
    #                         if parts:
    #                             parts = parts.groupdict()
    #                             code = parts['code'].upper()
    #                             aor_records = AOR.objects.filter(equip_code__exact=code)
    #
    #                             if aor_records.count() >= 1:
    #                                 aor = aor_records[0]
    #
    #                         Tasks.objects.update_or_create(work_order=row['Work Order'],
    #                                                        defaults={'line': '1',
    #                                                                  'equipment': row['Charge To Name'],
    #                                                                  'AOR': aor,
    #                                                                  'description': row['Description'],
    #                                                                  'work_type': 'CM',
    #                                                                  'priority': row['Priority'],
    #                                                                  'kitted_date': row['Date Kitted'],
    #                                                                  'requested_by': row['Requested by'],
    #                                                                  'estimate_hour': timedelta(
    #                                                                      hours=int(row['Man Hrs'])),
    #                                                                  'current_status': 'new'
    #                                                                  })
    #
    #                 # update documents
    #                 Documents.objects.filter(id=file.id).update(status='loaded')
    #
    #                 return JsonResponse({})
    #     else:
    #         return JsonResponse({})



if __name__ == '__main__':
    path = os.path.join(BASE_DIR, 'WorkSchedule/WorkConfig/sample/config/Approved.csv')
    TasksLoadProcessor.tasks_load_processor(path)