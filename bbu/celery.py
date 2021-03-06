from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bbu.settings')

app = Celery('bbu')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.conf.timezone = 'America/New_York'

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# time in UTC
# app.conf.beat_schedule = {
#     'sync_equipment': {
#         'task': 'spider.somax.tasks.sync_equipment',
#         'schedule': crontab(minute=0, hour=0),
#         'args': (),
#     },
#     'sync_pm': {
#         'task': 'spider.somax.tasks.sync_pm',
#         'schedule': crontab(minute=0, hour=2),
#         'args': (),
#     },
#     'sync_task': {
#         'task': 'spider.somax.tasks.sync_task',
#         'schedule': crontab(minute=0, hour=3),
#         'args': (),
#     },
#     # 'test': {
#     #     'task': 'spider.somax.tasks.test_task',
#     #     'schedule': crontab(minute='*', hour='*'),
#     #     'args': (),
#     # },
# }


def is_available_workers():
    result = app.control.inspect().ping()
    if result:
        count = 0
        for key, value in result.items():
            if value['ok'] == 'pong':
                count += 1
        if count >= 1:
            result = True
        else:
            result = False
    else:
        result = False
    return result
