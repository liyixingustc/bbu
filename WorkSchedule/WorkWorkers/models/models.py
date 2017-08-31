from django.db import models
from django.utils import timezone

from accounts.models import User
from ...WorkConfig.models.models import *
from ...WorkTasks.models.models import *

from configuration.WorkScheduleConstants import WorkAvailSheet
import datetime

# Create your models here.

source_choice = (('manual', 'manual'),
                 ('file', 'file'),
                 ('somax', 'somax'),
                )

current_status_choice = (('Working', 'Working'),
                         ('Canceled', 'Canceled'),
                         ('Complete', 'Complete'),
                         ('Uncomplete', 'Uncomplete'),
                         )


class WorkerAvailable(models.Model):

    name = models.ForeignKey(Workers, verbose_name='name', db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=0))
    duration_actual = models.DurationField(default=timedelta(hours=0))
    deduction = models.DurationField(default=WorkAvailSheet.DEDUCTION)
    time_start = models.DateTimeField(default=timezone.now)
    time_end = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, db_column='created_by', default=1)
    created_on = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=100, choices=source_choice, default='manual')
    document = models.ForeignKey(Documents, db_column='document', to_field='name', null=True, blank=True)


class WorkerScheduled(models.Model):

    name = models.ForeignKey(Workers, db_column='name', to_field='name')
    date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=0))
    time_start = models.DateTimeField(default=timezone.now)
    time_end = models.DateTimeField(default=timezone.now)
    task_id = models.ForeignKey(Tasks, db_column='task_id')
    available_id = models.ForeignKey(WorkerAvailable, db_column='available_id')
    created_by = models.ForeignKey(User, db_column='created_by', default=1)
    created_on = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=100, choices=source_choice, default='manual')
    document = models.ForeignKey(Documents, db_column='document', to_field='name', null=True, blank=True)
    current_status = models.CharField(max_length=100, choices=source_choice, default='manual')

# class WorkerActual(models.Model):
#
#     name = models.ForeignKey(Workers, db_column='name', to_field='name')
#     date = models.DateField()
#     duration = models.DurationField(default=timedelta(hours=0))
#     time_start = models.DateTimeField(default=timezone.now)
#     time_end = models.DateTimeField(default=timezone.now)
#     task_id = models.ForeignKey(Tasks, db_column='task_id')
#     created_by = models.ForeignKey(User, db_column='created_by', default=1)
#     created_on = models.DateTimeField(default=timezone.now)
#     source = models.CharField(max_length=10, choices=source_choice, default='manual')
#     document = models.ForeignKey(Documents, db_column='document', to_field='name', null=True, blank=True)

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

