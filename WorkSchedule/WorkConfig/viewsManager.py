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

# import processor
from .processor.TasksLoadProcessor import TasksLoadProcessor
from .processor.WorkerAvailLoadProcessor import WorkerAvailLoadProcessor
from .processor.AORLoadProcessor import AORLoadProcessor
from .processor.CompanyLoadProcessor import CompanyLoadProcessor
from .processor.EquipmentLoadProcessor import EquipmentLoadProcessor
from .processor.PMsLoadProcessor import PMsLoadProcessor
from .processor.SomaxAccountLoadProcessor import SomaxAccountLoadProcessor
from .processor.WorkerLoadProcessor import WorkerLoadProcessor


EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class FormManager:

            media_input_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/input.xlsx')

            @classmethod
            def submit(cls, request, *args, **kwargs):
                file_type = request.GET.get('FileType')

                if file_type == 'Tasks':
                    TasksLoadProcessor.tasks_load_processor()
                elif file_type == 'WorkerAvail':
                    WorkerAvailLoadProcessor.worker_avail_load_processor(request)
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