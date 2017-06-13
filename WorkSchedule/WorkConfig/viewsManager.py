import os
from django.http import JsonResponse
import pandas as pd

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *


class PageManager:

    class PanelManager:
        class FormManager:

            media_input_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/input.xlsx')

            @classmethod
            def submit(cls,request, *args, **kwargs):
                file_type = request.GET.get('FileType')
                as_of_date = request.GET.get('AsOfDate')

                if os.path.exists(cls.media_input_filepath):
                    data = pd.read_excel(cls.media_input_filepath)
                else:
                    return JsonResponse({})

                if file_type == 'Tasks':
                    cls.tasks_load(data, as_of_date)
                elif file_type == 'WorkerAvail':
                    cls.worker_avail_load(data)

                return JsonResponse({})

            @classmethod
            def tasks_load(cls, data, as_of_date):
                print(data)

            @classmethod
            def worker_avail_load(cls, data):
                pass

            @classmethod
            def fileupload(cls,request, *args, **kwargs):
                file = request.FILES.get('FileUpload')
                with open(cls.media_input_filepath, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                return JsonResponse({})