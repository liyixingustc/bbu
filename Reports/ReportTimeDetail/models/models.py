from django.db import models
from django.utils import timezone
from accounts.models import User

import pytz
from dateutil import tz
import datetime

from configuration.ModelChoiceConstants import BaseConstants
# Create your models here.


class ReportLostTimeDetail(models.Model):
    SalesDate = models.DateTimeField(default=timezone.now)
    Line = models.CharField(max_length=100, null=True, blank=True, choices=BaseConstants.line_choice)
    Shift = models.CharField(max_length=100, null=True, blank=True, choices=BaseConstants.shift_choice)
    OracleType = models.CharField(max_length=100, null=True, blank=True)
    MIPS_Description = models.CharField(max_length=100, null=True, blank=True)
    LostTimeMinutes = models.FloatField(null=True, blank=True)
    LostTimeValue = models.FloatField(null=True, blank=True)
    Occ = models.FloatField(null=True, blank=True)
    OracleCategory = models.CharField(max_length=100, null=True, blank=True)
    Category = models.CharField(max_length=100, null=True, blank=True)
    Area = models.CharField(max_length=100, null=True, blank=True)
    Cause = models.CharField(max_length=100, null=True, blank=True)
    Comments = models.CharField(max_length=100, null=True, blank=True)
    LineStop = models.CharField(max_length=100, null=True, blank=True)
    Init = models.CharField(max_length=100, null=True, blank=True)


class ReportTimeDetail(models.Model):
    SalesDate = models.DateTimeField(default=timezone.now)
    Line = models.CharField(max_length=100, null=True, blank=True, choices=BaseConstants.line_choice)
    Shift = models.CharField(max_length=100, null=True, blank=True, choices=BaseConstants.shift_choice)
    OracleType = models.CharField(max_length=100, null=True, blank=True)
    OracleFormula = models.CharField(max_length=100, null=True, blank=True)
    MIPS_Description = models.CharField(max_length=100, null=True, blank=True)
    SchedChangeOverTime_min = models.FloatField(null=True, blank=True)
    OracleTheoChangeOverTime_min = models.FloatField(null=True, blank=True)
    ActualChangeOverTime_min = models.FloatField(null=True, blank=True)
    Init = models.CharField(max_length=100, null=True, blank=True)
    WrappingStartDateTime = models.CharField(max_length=100, null=True, blank=True)
    WrappingEndDateTime = models.CharField(max_length=100, null=True, blank=True)
    MechLostTime_min = models.FloatField(null=True, blank=True)
    SchedLostTime_min = models.FloatField(null=True, blank=True)
    AOLostTime_min = models.FloatField(null=True, blank=True)
    ActualRunTime_min = models.FloatField(null=True, blank=True)
    TotalLostTime_min = models.FloatField(null=True, blank=True)
    OracleAOLostTime_min = models.FloatField(null=True, blank=True)
    TheoRunTime_min = models.FloatField(null=True, blank=True)
    EngTheoRunTime_min = models.FloatField(null=True, blank=True)
    TimeVar_min = models.FloatField(null=True, blank=True)
    TimeVar_perc = models.FloatField(null=True, blank=True)
