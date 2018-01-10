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

    somax_spider = SomaxSpider()

    try:
        somax_spider.task_spider()
    except Exception as e:
        print(e)
    finally:
        somax_spider.close()

    # from WorkSchedule.WorkConfig.processor.TasksLoadProcessor import TasksLoadProcessor
    # import os
    # file_path = os.path.join('/home/arthurtu/projects/bbu/media/spider/somax/task/WorkOrderSearch.csv')
    # TasksLoadProcessor.tasks_load_processor([file_path])
    return


@app.task
def sync_schedules_to_somax():

    somax_spider = SomaxSpider()

    try:
        somax_spider.sync_schedules_to_somax_spider()
    except Exception as e:
        print(e)
    finally:
        somax_spider.close()

    return


@app.task
def test_task():
    time.sleep(1)
    return

if __name__ == '__main__':
    # sync_task.delay()
    import sys
    sys.path.append('/home/arthurtu/projects/bbu')
    test_task.delay()