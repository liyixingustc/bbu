from bbu.celery import app
from celery import shared_task
import time

from .utils.SmartScheduler import SmartScheduler


@app.task
def auto_schedule(work_orders=None):

    SmartScheduler(work_orders=work_orders).run()

    return