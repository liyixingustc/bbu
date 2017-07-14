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

from .processor.TasksLoadProcessor import TasksLoadProcessor
from .processor.WorkerAvailLoadProcessor import WorkerAvailLoadProcessor

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
                    WorkerAvailLoadProcessor.worker_avail_processor()

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
            def fileupload(cls,request, *args, **kwargs):
                files = request.FILES.getlist('FileUpload')
                if request.method == 'POST' and files:
                    FileType = request.POST.get('FileType')
                    Processor = request.POST.get('Processor')
                    if files:
                        for file in files:
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