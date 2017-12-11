import sys
import os

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

from datetime import datetime as dt, timedelta

import django
from bbu.settings import BASE_DIR, MEDIA_ROOT

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbu.settings'
django.setup()

from WorkSchedule.WorkTasks.models.models import *


class DataInit:

    @classmethod
    def task_init(cls):

        # init lunch
        Tasks.objects.update_or_create(
            work_order='TLUNCH',
            defaults={
                'description': 'Lunch Time',
                'work_type': None,
                'current_status': 'Complete',
                'line': None,
                'shift': None,
                'priority': 'T',
                'create_date': None,
                'current_status_somax': 'Complete',
                'schedule_date_somax': None,
                'actual_date_somax': None,
                'estimate_hour': timedelta(minutes=30),
                'scheduled_hour': timedelta(hours=0),
                'actual_hour': timedelta(hours=0),
                'fail_code': None,
                'completion_comments': None,
                'equipment': None,
                'AOR': None,
                'creator': None,
                'assigned': None,
                'PMs': None,
                'source': 'auto',
                'document': None,
                'parts_location': None
            })

        # init break
        Tasks.objects.update_or_create(
            work_order='TBREAK',
            defaults={
                'description': 'Break Time',
                'work_type': None,
                'current_status': 'Complete',
                'line': None,
                'shift': None,
                'priority': 'T',
                'create_date': None,
                'current_status_somax': 'Complete',
                'schedule_date_somax': None,
                'actual_date_somax': None,
                'estimate_hour': timedelta(minutes=15),
                'scheduled_hour': timedelta(hours=0),
                'actual_hour': timedelta(hours=0),
                'fail_code': None,
                'completion_comments': None,
                'equipment': None,
                'AOR': None,
                'creator': None,
                'assigned': None,
                'PMs': None,
                'source': 'auto',
                'document': None,
                'parts_location': None
            })

        # init union business
        Tasks.objects.update_or_create(
            work_order='OUNIONBUSS',
            defaults={
                'description': 'Break Time',
                'work_type': None,
                'current_status': 'Complete',
                'line': None,
                'shift': None,
                'priority': 'T',
                'create_date': None,
                'current_status_somax': 'Complete',
                'schedule_date_somax': None,
                'actual_date_somax': None,
                'estimate_hour': timedelta(hours=0),
                'scheduled_hour': timedelta(hours=0),
                'actual_hour': timedelta(hours=0),
                'fail_code': None,
                'completion_comments': None,
                'equipment': None,
                'AOR': None,
                'creator': None,
                'assigned': None,
                'PMs': None,
                'source': 'auto',
                'document': None,
                'parts_location': None
            })

    @classmethod
    def init(cls):
        cls.task_init()


if __name__ == '__main__':

    DataInit.init()