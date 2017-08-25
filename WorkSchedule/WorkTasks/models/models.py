from django.db import models
from datetime import timedelta

from ...WorkConfig.models.models import *

from configuration.ModelChoiceConstants import BaseConstants

# Create your models here.

status_choice = (('Approved', 'Approved'),
                 ('Canceled', 'Canceled'),
                 ('Complete', 'Complete'),
                 ('Denied', 'Denied'),
                 ('Scheduled', 'Scheduled'),
                 ('Work Request', 'Work Request'),
                 )

working_type_choice = (('CM', 'CM'),
                       ('PM', 'PM'),
                       ('EV', 'EV'),
                       ('EM', 'EM'),)

priority_choice = (('s', 's'),
                   ('u', 'u'),
                   ('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('4', '4'),
                   ('T', 'T'),
                   ('O', 'O'),
                   )


class Tasks(models.Model):

    # model fields
    work_order = models.CharField(max_length=30)
    description = models.CharField(max_length=150, null=True, blank=True)
    work_type = models.CharField(max_length=10, choices=working_type_choice, null=True, blank=True)
    current_status = models.CharField(max_length=10, choices=status_choice, default='Work Request')
    line = models.CharField(max_length=10, choices=BaseConstants.line_choice, null=True, blank=True)
    shift = models.CharField(max_length=10, choices=BaseConstants.shift_choice, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=priority_choice, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)

    schedule_date = models.DateTimeField(null=True, blank=True)
    actual_date = models.DateTimeField(null=True, blank=True)
    estimate_hour = models.DurationField(default=timedelta(hours=0))

    fail_code = models.CharField(max_length=50, null=True, blank=True)
    completion_comments = models.CharField(max_length=150, null=True, blank=True)

    equipment = models.ForeignKey(Equipment, )
    AOR = models.ForeignKey(AOR, db_column='AOR', null=True, blank=True)
    creator = models.ForeignKey(SomaxAccount, db_column='creator', related_name='Tasks_creator', null=True, blank=True)
    assigned = models.ForeignKey(SomaxAccount, db_column='assigned', related_name='Tasks_assigned', null=True, blank=True)


class PMs(models.Model):

    masterjob_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    schedule_type = models.CharField(max_length=100, null=True, blank=True)
    duration = models.DurationField(default=timedelta(hours=0))
    PMs_type = models.CharField(max_length=100, null=True, blank=True)