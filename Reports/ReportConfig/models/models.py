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

file_type_choice = (('ReportTimeDetail', 'ReportTimeDetail'),
                    )

processor_choice = (('ReportTimeDetailProcessor', 'ReportTimeDetailProcessor'),
                    )


class Documents(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    datetime = models.DateTimeField(default=timezone.now)
    document = models.FileField(upload_to='Reports/ReportConfig/excel')
    file_type = models.CharField(max_length=30, choices=file_type_choice, null=True, blank=True)
    processor = models.CharField(max_length=50, choices=processor_choice, null=True, blank=True)
    status = models.CharField(default='new', max_length=30, choices=document_status_choice)
    created_by = models.ForeignKey(User, db_column='created_by', default=1, related_name='ReportConfig')
    created_on = models.DateTimeField(default=timezone.now)
