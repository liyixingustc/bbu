from bbu.celery import app
from celery import shared_task
import time

from WorkSchedule.WorkConfig.processor.WorkerAvailLoadProcessor import *


@app.task
def WorkScheduleWorkerAvailLoadProcessorAddDefaultTasks(data=None):
    if data:
        for task in data:
            WorkerAvailLoadProcessor.add_default_task(
                task['request'],
                task['worker'],
                task['date'],
                task['start'],
                task['end'],
                task['duration'],
                task['file'],
                task['available_id'],
                task['is_union_bus'],
            )

    return