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

from utils.UDatetime import UDatetime

EST = pytz.timezone(TIME_ZONE)


class TasksLoadProcessor:

    @classmethod
    def tasks_load_processor(cls):

        files = Documents.objects.filter(status__exact='new', file_type__exact='Tasks')
        if files.exists():
            for file in files:
                path = BASE_DIR + file.document.url
                if os.path.exists(path):
                    data = pd.read_csv(path, encoding='iso-8859-1')

                    data['Created'] = pd.to_datetime(data['Created'], format='%m/%d/%Y')
                    data['Created'] = data['Created'].apply(lambda x: UDatetime.localize(x))

                    data['Scheduled'] = pd.to_datetime(data['Scheduled'], format='%m/%d/%Y')
                    data['Scheduled'] = data['Scheduled'].apply(lambda x: UDatetime.localize(x))

                    data['Actual Finish'] = pd.to_datetime(data['Actual Finish'], format='%m/%d/%Y')
                    data['Actual Finish'] = data['Actual Finish'].apply(lambda x: UDatetime.localize(x))

                    for index, row in data.iterrows():

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

                        estimate_hour = PMs.objects.filter(description__exact=row['Description'])
                        if estimate_hour.exists():
                            est = estimate_hour[0].duration
                        else:
                            est = timedelta(hours=0)

                        Tasks.objects.update_or_create(work_order=row['Work Order'],
                                                       defaults={
                                                                 'description': row['Description'],
                                                                 'work_type': row['Type'],
                                                                 'current_status_somax': row['Status'],
                                                                 'line': None,
                                                                 'shift': row['Shift'],
                                                                 'priority': row['Priority'],
                                                                 'create_date': row['Created'],
                                                                 'schedule_date_somax': row['Scheduled'],
                                                                 'actual_date_somax': row['Actual Finish'],
                                                                 'estimate_hour': est,
                                                                 'fail_code': row['Fail Code'],
                                                                 'completion_comments': row['Completion Comments'],
                                                                 'equipment': equipment,
                                                                 'AOR': aor,
                                                                 'creator': creator,
                                                                 'assigned': assigned,
                                                                 })

                    # update documents
                    Documents.objects.filter(id=file.id).update(status='loaded')

                    return JsonResponse({})
        else:
            return JsonResponse({})

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