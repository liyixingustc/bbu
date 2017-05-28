from django.db import models
from datetime import timedelta

# Create your models here.


class Tasks(models.Model):

    working_type_choice = (('CM', 'CM'),
                           ('PM', 'PM'),
                           ('EV', 'EV'),
                           ('EM', 'EM'),)

    priority_choice = (('s', 's'),
                       ('u', 'u'),
                       ('1', '1'),
                       ('2', '2'),
                       ('3', '3'),
                       ('4', '4'),)

    #model fields
    working_order = models.CharField(max_length=30, null=True)
    line = models.CharField(max_length=10, null=True)
    description = models.CharField(max_length=150, null=True)
    working_type = models.CharField(max_length=10, choices=working_type_choice, null=True)
    priority = models.CharField(max_length=10, choices=priority_choice, null=True)
    days_old = models.DurationField(default=timedelta(days=0))
    period_start = models.DateTimeField(null=True)
    period_end = models.DateTimeField(null=True)
    estimate_hour = models.DurationField(default=timedelta(hours=0))
    schedule_hour = models.DurationField(default=timedelta(hours=0))
    actual_hour = models.DurationField(default=timedelta(hours=0))
