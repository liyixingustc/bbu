from bbu.celery import app
from celery import shared_task
import time

from Reports.ReportConfig.processor.ReportLostTimeDetailProcessor import ReportLostTimeDetailProcessor


@app.task
def ReportLostTimeDetailProcessorTask():
    ReportLostTimeDetailProcessor.report_lost_time_detail_processor()

    return