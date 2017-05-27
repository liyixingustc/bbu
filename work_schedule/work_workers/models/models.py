from django.db import models
from ...work_config.models.models import *
from ...work_tasks.models.models import *

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
    task = models.ManyToManyField(Tasks)


class WorkerActual(models.Model):

    name = models.ForeignKey(workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField()
    time = models.CharField(max_length=100)
    task = models.ManyToManyField(Tasks)


# class WorkerRecords(models.Model):
#     name = models.OneToOneField(workers, db_column='name')





