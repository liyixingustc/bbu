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
                 ('Wait For Parts', 'Wait For Parts'),
                 )

working_type_choice = (('CM', 'CM'),
                       ('PM', 'PM'),
                       ('EV', 'EV'),
                       ('EM', 'EM'),
                       (None, None),
                       )

priority_choice = (('s', 's'),
                   ('u', 'u'),
                   ('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('4', '4'),
                   ('T', 'T'),
                   ('O', 'O'),
                   (None, None),
                   )

sync_to_somax_choice = (('yes', 'yes'),
                        ('no', 'no'),
                        ('error', 'error'),
                        )


class PMs(models.Model):

    masterjob_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    schedule_type = models.CharField(max_length=100, null=True, blank=True)
    duration = models.DurationField(default=timedelta(hours=0))
    PMs_type = models.CharField(max_length=100, null=True, blank=True)
    due_days = models.DurationField(default=timedelta(days=0), null=True, blank=True)


class Tasks(models.Model):

    # model fields
    work_order = models.CharField(max_length=30)
    description = models.CharField(max_length=3000, null=True, blank=True)
    work_type = models.CharField(max_length=10, choices=working_type_choice, null=True, blank=True)
    current_status = models.CharField(max_length=30, choices=status_choice, default='Work Request')
    line = models.CharField(max_length=10, choices=BaseConstants.line_choice, null=True, blank=True)
    shift = models.CharField(max_length=10, choices=BaseConstants.shift_choice, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=priority_choice, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)

    current_status_somax = models.CharField(max_length=30, choices=status_choice, default='Work Request')
    schedule_date_somax = models.DateTimeField(null=True, blank=True)
    actual_date_somax = models.DateTimeField(null=True, blank=True)
    estimate_hour = models.DurationField(default=timedelta(hours=0))
    scheduled_hour = models.DurationField(default=timedelta(hours=0))
    actual_hour = models.DurationField(default=timedelta(hours=0))

    parts_location = models.CharField(max_length=100, null=True, blank=True)

    fail_code = models.CharField(max_length=100, null=True, blank=True)
    completion_comments = models.CharField(max_length=150, null=True, blank=True)

    equipment = models.ForeignKey(Equipment, db_column='equipment', null=True, blank=True)
    AOR = models.ForeignKey(AOR, db_column='AOR', null=True, blank=True)
    creator = models.ForeignKey(SomaxAccount, db_column='creator', related_name='Tasks_creator', null=True, blank=True)
    assigned = models.ForeignKey(SomaxAccount, db_column='assigned', related_name='Tasks_assigned', null=True, blank=True)
    PMs = models.ForeignKey(PMs, db_column='PMs', null=True, blank=True)

    created_by = models.ForeignKey(User, db_column='created_by', default=1)
    created_on = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=100, choices=BaseConstants.source_choice, default='manual')
    document = models.ForeignKey(Documents, db_column='document', to_field='name', null=True, blank=True)

    sync_to_somax = models.CharField(max_length=20, choices=sync_to_somax_choice, null=True, blank=True)
