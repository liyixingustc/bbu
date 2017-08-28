from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime

from configuration.ModelChoiceConstants import BaseConstants
# Create your models here.

document_status_choice = (('new', 'new'),
                          ('loaded', 'loaded'),
                          )

file_type_choice = (('Tasks', 'Tasks'),
                    ('WorkerAvail', 'WorkerAvail'),
                    ('AOR', 'AOR'),
                    ('Company', 'Company'),
                    ('Equipment', 'Equipment'),
                    ('PMs', 'WorkerAvail'),
                    ('SomaxAccount', 'SomaxAccount'),
                    ('Worker', 'Worker'),
                    )

processor_choice = (('TasksLoadProcessor', 'TasksLoadProcessor'),
                    ('WorkerAvailLoadProcessor', 'WorkerAvailLoadProcessor'),
                    ('AORLoadProcessor', 'AORLoadProcessor'),
                    ('CompanyLoadProcessor', 'CompanyLoadProcessor'),
                    ('EquipmentLoadProcessor', 'EquipmentLoadProcessor'),
                    ('PMsLoadProcessor', 'PMsLoadProcessor'),
                    ('SomaxAccountLoadProcessor', 'SomaxAccountLoadProcessor'),
                    ('WorkerLoadProcessor', 'WorkerLoadProcessor'),
                    )

level_choice = (('lead', 'lead'),
                ('worker', 'worker'),
                )

worker_status_choice = (('active', 'active'),
                        ('inactive', 'inactive'),
                        )

worker_type_choice = (('employee', 'employee'),
                      ('contractor', 'contractor'),
                      ('none', 'none'),
                      )

AOR_type_choice = (('major', 'major'),
                   ('minor', 'minor'),
                   )


class SomaxAccount(models.Model):

    user_name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    security_profile = models.CharField(max_length=100, null=True, blank=True)
    user_type = models.CharField(max_length=100, null=True, blank=True)


class Company(models.Model):
    business_name = models.CharField(max_length=30, unique=True)
    address = models.CharField(max_length=100)


class Equipment(models.Model):
    equipment_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    equipment_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    serial_no = models.CharField(max_length=100, null=True, blank=True)
    equipment_type = models.CharField(max_length=100, null=True, blank=True)
    make = models.CharField(max_length=100, null=True, blank=True)
    model_no = models.CharField(max_length=100, null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True)
    asset_number = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    line = models.CharField(max_length=100, null=True, blank=True)
    equipment_name_clean = models.CharField(max_length=100, null=True, blank=True)


class Workers(models.Model):

    name = models.CharField(max_length=30, unique=True)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    company = models.ForeignKey(Company, to_field='business_name', db_column='company')
    level = models.CharField(default='lead', max_length=30, choices=level_choice)
    shift = models.CharField(default='1', max_length=30, choices=BaseConstants.shift_choice)
    status = models.CharField(default='active', max_length=30, choices=worker_status_choice)
    type = models.CharField(default='employee', max_length=30, choices=worker_type_choice)
    somax_account = models.ForeignKey(SomaxAccount, to_field='user_name', db_column='somax_account', null=True, blank=True)


class Documents(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    datetime = models.DateTimeField(default=timezone.now)
    document = models.FileField(upload_to='WorkSchedule/WorkConfig/excel')
    file_type = models.CharField(max_length=30, choices=file_type_choice, null=True, blank=True)
    processor = models.CharField(max_length=50, choices=processor_choice, null=True, blank=True)
    status = models.CharField(default='new', max_length=30, choices=document_status_choice)
    created_by = models.ForeignKey(User, db_column='created_by', default=1, related_name='WorkConfig')
    created_on = models.DateTimeField(default=timezone.now)


class AOR(models.Model):

    worker = models.ForeignKey(Workers, to_field='name', db_column='name')
    line = models.CharField(max_length=30, choices=BaseConstants.line_choice, null=True, blank=True)
    AOR_type = models.CharField(max_length=30, choices=AOR_type_choice, null=True, blank=True)
    equip_name = models.CharField(max_length=100)
    equip_code = models.CharField(max_length=100)
    equip_id = models.ForeignKey(Equipment, db_column='equipment_id', null=True, blank=True)