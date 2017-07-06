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


class Company(models.Model):
    business_name = models.CharField(max_length=30,unique=True)
    address = models.CharField(max_length=30,unique=True)


class Workers(models.Model):

    name = models.CharField(max_length=30,unique=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    company = models.ForeignKey(Company,to_field='business_name', null=True, blank=True)


class Documents(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True, unique=True)
    datetime = models.DateTimeField(default=timezone.now)
    document = models.FileField(upload_to='WorkSchedule/WorkConfig/excel')
    file_type = models.CharField(default='new', max_length=30, choices=file_type_choice, null=True, blank=True,)
    processor = models.CharField(default='new', max_length=30, choices=processor_choice, null=True, blank=True,)
    status = models.CharField(default='new', max_length=30, choices=document_status_choice)
    created_by = models.ForeignKey(User, db_column='created_by', default=1)
    created_on = models.DateTimeField(default=timezone.now)


