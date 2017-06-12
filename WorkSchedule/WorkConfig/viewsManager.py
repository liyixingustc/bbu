from django.http import JsonResponse
import pandas as pd

from ..WorkWorkers.models.models import *
from ..WorkTasks.models.models import *

class PageManager:

    class PanelManager:
        class TimeLineManager:
            @staticmethod
            def resources(request, *args, **kwargs):
                date = request.GET.get('start')
                workers = Workers.objects.all().values()
                records = pd.DataFrame.from_records(workers)
                records.rename_axis({'name':'title'},axis=1,inplace=True)
                response = records.to_dict(orient='records')
                return JsonResponse(response,safe=False)

            @staticmethod
            def events(request, *args, **kwargs):
                date = request.GET.get('start')

                return JsonResponse({})