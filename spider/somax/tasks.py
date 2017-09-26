from bbu.celery import app
from celery import shared_task
import time

from .somax_spider import SomaxSpider
# from spider.somax.somax_spider import SomaxSpider


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
    return
