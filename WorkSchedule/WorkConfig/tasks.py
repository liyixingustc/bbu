from bbu.celery import app
from celery import shared_task
import time

from WorkSchedule.WorkConfig.processor.WorkerAvailLoadProcessor import WorkerAvailLoadProcessor


@app.task
def WorkerAvailLoadProcessorTask(usr_id):
    WorkerAvailLoadProcessor.worker_avail_load_processor(usr_id)

    return