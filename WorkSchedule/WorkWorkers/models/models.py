from django.db import models
from ...WorkConfig.models.models import *
from ...WorkTasks.models.models import *

# Create your models here.


class WorkerAvailable(models.Model):

    name = models.ForeignKey(workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField()
    time = models.CharField(max_length=100)


class WorkerScheduled(models.Model):

    name = models.ForeignKey(workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField()
    time = models.CharField(max_length=100)
    task = models.ManyToManyField(Tasks, through='WorkerScheduledTask')


class WorkerActual(models.Model):

    name = models.ForeignKey(workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField()
    time = models.CharField(max_length=100)
    task = models.ManyToManyField(Tasks, through='WorkerActualTask')


class WorkerScheduledTask(models.Model):

    workerscheduled_id = models.ForeignKey(WorkerScheduled, db_column='workerscheduled_id')
    task_id = models.ForeignKey(Tasks, db_column='task_id')
    created_on = models.DateTimeField(auto_now_add=True)


class WorkerActualTask(models.Model):

    workeractual_id = models.ForeignKey(WorkerActual, db_column='workeractual_id')
    task_id = models.ForeignKey(Tasks, db_column='task_id')
    created_on = models.DateTimeField(auto_now_add=True)







