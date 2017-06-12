import os
from django.http import JsonResponse
import pandas as pd

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *

class PageManager:

    class PanelManager:
        class FormManager:
            @staticmethod
            def submit(request, *args, **kwargs):
                date = request.GET.get('start')
                workers = Workers.objects.all().values()
                records = pd.DataFrame.from_records(workers)
                records.rename_axis({'name':'title'},axis=1,inplace=True)
                response = records.to_dict(orient='records')
                return JsonResponse(response,safe=False)

            @staticmethod
            def fileupload(request, *args, **kwargs):
                file = request.FILES.get('FileUpload')
                filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'media/input.xlsx')
                with open(filepath, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                return JsonResponse({})