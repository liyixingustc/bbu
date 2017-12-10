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
from Exception.Exception import ExceptionCustom
from utils.UDatetime import UDatetime

# import processor
from .processor.TasksLoadProcessor import TasksLoadProcessor
# from .processor.WorkerAvailLoadProcessor import WorkerAvailLoadProcessor
from .processor.AORLoadProcessor import AORLoadProcessor
from .processor.CompanyLoadProcessor import CompanyLoadProcessor
from .processor.EquipmentLoadProcessor import EquipmentLoadProcessor
from .processor.PMsLoadProcessor import PMsLoadProcessor
from .processor.SomaxAccountLoadProcessor import SomaxAccountLoadProcessor
from .processor.WorkerLoadProcessor import WorkerLoadProcessor
from .processor.PartsOpenProcessor import PartsOpenProcessor

from bbu.celery import is_available_workers
from .tasks import *


EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class FormManager:

            media_input_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/input.xlsx')
            result_path = os.path.join(BASE_DIR, 'WorkSchedule/WorkConfig/processor/result/result.csv')

            @classmethod
            def submit(cls, request, *args, **kwargs):
                file_type = request.GET.get('FileType')
                try:
                    if file_type == 'Tasks':
                        TasksLoadProcessor.tasks_load_processor()
                    elif file_type == 'WorkerAvail':
                        usr_id = request.user.id
                        # is_workers = is_available_workers()
                        # if not is_workers:
                        WorkerAvailLoadProcessor.worker_avail_load_processor(usr_id)
                        # else:
                        #     WorkerAvailLoadProcessorTask.delay(usr_id)
                    elif file_type == 'AOR':
                        AORLoadProcessor.aor_load_processor()
                    elif file_type == 'Company':
                        CompanyLoadProcessor.company_load_processor()
                    elif file_type == 'Equipment':
                        EquipmentLoadProcessor.equipment_load_processor()
                    elif file_type == 'PMs':
                        PMsLoadProcessor.pms_load_processor()
                    elif file_type == 'SomaxAccount':
                        SomaxAccountLoadProcessor.somax_account_load_processor()
                    elif file_type == 'Worker':
                        WorkerLoadProcessor.worker_load_processor()
                    elif file_type == 'PartsOpen':
                        PartsOpenProcessor.parts_open_processor()
                except Exception as e:
                    WorkerAvailLoadProcessor.update_process(None)
                    msg = ExceptionCustom.get_client_message(e)
                    print(e)
                    return JsonResponse({'status': 0, 'msg': msg})

                return JsonResponse({'status': 1, 'msg': ''})

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

            @classmethod
            def process(cls, request, *args, **kwargs):

                file_type = request.GET.get('FileType')

                if os.path.exists(cls.result_path):
                    result_df = pd.read_csv(cls.result_path)
                    result_bytype = result_df[result_df['filetype'] == file_type]
                    if result_bytype.empty:
                        result = None
                    else:
                        result = float(result_bytype['result'][0])
                        if pd.isnull(result):
                            result = None
                else:
                    result = None

                return JsonResponse({'result': result})