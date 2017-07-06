from django.db import models
from accounts.models import User

import datetime
# Create your models here.


class Company(models.Model):
    business_name = models.CharField(max_length=30,unique=True)
    address = models.CharField(max_length=30,unique=True)


class Workers(models.Model):

    name = models.CharField(max_length=30,unique=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    company = models.ForeignKey(Company,to_field='business_name', null=True, blank=True)


class Documents(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    document = models.FileField(upload_to='WorkSchedule/WorkConfig/excel')
    created_by = models.ForeignKey(User,default=1)
    created_on = models.DateTimeField(default=datetime.datetime.now)


