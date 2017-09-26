from bbu.celery import app
from celery import shared_task
import time

# from .somax_spider import SomaxSpider
from spider.somax.somax_spider import SomaxSpider


@app.task
def sync_equipment():
    SomaxSpider().equipment_spider()
    return


@app.task
def sync_pm():
    SomaxSpider().pm_spider()
    return


@app.task
def sync_task():
    SomaxSpider().task_spider()

    # from WorkSchedule.WorkConfig.processor.TasksLoadProcessor import TasksLoadProcessor
    # import os
    # file_path = os.path.join('/home/arthurtu/projects/bbu/media/spider/somax/task/WorkOrderSearch.csv')
    # TasksLoadProcessor.tasks_load_processor([file_path])
    return

if __name__ == '__main__':
    sync_task.delay()