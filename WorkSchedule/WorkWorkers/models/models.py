from django.db import models

from accounts.models import User
from ...WorkConfig.models.models import *
from ...WorkTasks.models.models import *

from configuration.WorkScheduleConstants import WorkAvailSheet
import datetime

# Create your models here.


class WorkerAvailable(models.Model):

    name = models.ForeignKey(Workers, verbose_name='name', db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=0))
    deduction = models.DurationField(default=WorkAvailSheet.DEDUCTION)
    time_start = models.DateTimeField(default=datetime.datetime.now)
    time_end = models.DateTimeField(default=datetime.datetime.now)
    created_by = models.ForeignKey(User,default=1)
    created_on = models.DateTimeField(default=datetime.datetime.now)


class WorkerScheduled(models.Model):

    name = models.ForeignKey(Workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=0))
    deduction = models.DurationField(default=WorkAvailSheet.DEDUCTION)
    time_start = models.DateTimeField(default=datetime.datetime.now)
    time_end = models.DateTimeField(default=datetime.datetime.now)
    task_id = models.ForeignKey(Tasks, db_column='task_id')
    created_by = models.ForeignKey(User,default=1)
    created_on = models.DateTimeField(default=datetime.datetime.now)


class WorkerActual(models.Model):

    name = models.ForeignKey(Workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=0))
    deduction = models.DurationField(default=WorkAvailSheet.DEDUCTION)
    time_start = models.DateTimeField(default=datetime.datetime.now)
    time_end = models.DateTimeField(default=datetime.datetime.now)
    task_id = models.ForeignKey(Tasks, db_column='task_id')
    created_by = models.ForeignKey(User, default=1)
    created_on = models.DateTimeField(default=datetime.datetime.now)

#
# class WorkerScheduledTask(models.Model):
#
#     workerscheduled_id = models.ForeignKey(WorkerScheduled, db_column='workerscheduled_id')
#     task_id = models.ForeignKey(Tasks, db_column='task_id')
#     created_on = models.DateTimeField(auto_now_add=True)

#
# class WorkerActualTask(models.Model):
#
#     workeractual_id = models.ForeignKey(WorkerActual, db_column='workeractual_id')
#     task_id = models.ForeignKey(Tasks, db_column='task_id')
#     created_on = models.DateTimeField(auto_now_add=True)

