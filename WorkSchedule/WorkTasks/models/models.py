from django.db import models
from datetime import timedelta

# Create your models here.

status_choice = (('new', 'new'),
                 ('pending', 'pending'),
                 ('completed', 'completed'),
                 ('cancelled', 'cancelled'),)


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

    line_choice = (('1', '1'),
                   ('2', '2'),
                   ('3', '3'),
                   ('7', '7'),
                   ('8', '8'),)


    #model fields
    work_order = models.CharField(max_length=30, null=True)
    line = models.CharField(max_length=10, null=True)
    equipment = models.CharField(max_length=10, null=True)
    description = models.CharField(max_length=150, null=True)
    work_type = models.CharField(max_length=10, choices=working_type_choice, null=True)
    priority = models.CharField(max_length=10, choices=priority_choice, null=True)
    days_old = models.DurationField(default=timedelta(days=0))
    create_time = models.DateTimeField(null=True)
    requested_by = models.CharField(max_length=30, null=True)
    estimate_hour = models.DurationField(default=timedelta(hours=0))
    schedule_hour = models.DurationField(default=timedelta(hours=0))
    actual_hour = models.DurationField(default=timedelta(hours=0))
    current_status = models.CharField(max_length=10,choices=status_choice)

class TasksStatus(models.Model):

    task_id = models.ForeignKey(Tasks, db_column='task_id')
    status = models.CharField(max_length=10,choices=status_choice)
    status_time = models.DateTimeField(auto_now_add=True)
