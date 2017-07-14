from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime
# Create your models here.

document_status_choice = (('new', 'new'),
                          ('loaded', 'loaded'),
                          )

file_type_choice = (('Tasks', 'Tasks'),
                    ('WorkerAvail', 'WorkerAvail'),
                    )

processor_choice = (('TasksLoadProcessor', 'TasksLoadProcessor'),
                    ('WorkerAvailProcessor', 'WorkerAvailProcessor'),
                    )

level_choice = (('lead', 'lead'),
                ('worker', 'worker'),
                )

shift_choice = (('1', '1'),
                ('2', '2'),
                ('3', '3'),
                )


class Company(models.Model):
    business_name = models.CharField(max_length=30,unique=True)
    address = models.CharField(max_length=100)


class Workers(models.Model):

    name = models.CharField(max_length=30,unique=True)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    company = models.ForeignKey(Company,to_field='business_name', db_column='company')
    level = models.CharField(default='lead', max_length=30, choices=level_choice)
    shift = models.CharField(default='1', max_length=30, choices=shift_choice)


class Documents(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    datetime = models.DateTimeField(default=timezone.now)
    document = models.FileField(upload_to='WorkSchedule/WorkConfig/excel')
    file_type = models.CharField(max_length=30, choices=file_type_choice, null=True, blank=True)
    processor = models.CharField(max_length=50, choices=processor_choice, null=True, blank=True)
    status = models.CharField(default='new', max_length=30, choices=document_status_choice)
    created_by = models.ForeignKey(User, db_column='created_by', default=1)
    created_on = models.DateTimeField(default=timezone.now)


