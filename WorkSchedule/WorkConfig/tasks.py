from bbu.celery import app
from celery import shared_task
import time

@app.task
def WorkScheduleWorkerAvailLoadProcessorAddDefaultTasks():


    return