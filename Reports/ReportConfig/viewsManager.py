import os
import numpy as np
import pandas as pd
import re
from datetime import datetime as dt
import pytz
import time

from bbu.settings import TIME_ZONE, BASE_DIR
from django.http import JsonResponse

from .models.models import *

from utils.UDatetime import UDatetime
from Exception.Exception import ExceptionCustom

from .processor.ReportTimeDetailProcessor import ReportTimeDetailProcessor
from .processor.ReportLostTimeDetailProcessor import ReportLostTimeDetailProcessor


EST = pytz.timezone(TIME_ZONE)


class PageManager:
    class PanelManager:
        class FormManager:

            @classmethod
            def submit(cls, request, *args, **kwargs):
                file_type = request.GET.get('FileType')
                if file_type == 'ReportLostTimeDetail':
                    try:
                        ReportLostTimeDetailProcessor.report_lost_time_detail_processor()
                    except Exception as e:
                        msg = ExceptionCustom.get_client_message(e)
                        return JsonResponse({'status': 0, 'msg': msg})
                elif file_type == 'ReportTimeDetail':
                    ReportTimeDetailProcessor.report_time_detail_processor()

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