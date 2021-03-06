# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-06-04 00:17
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WorkConfig', '0001_initial'),
        ('WorkTasks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerAvailable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('balance', models.DurationField(default=datetime.timedelta(0))),
                ('deduction', models.DurationField(default=datetime.timedelta(0, 3600))),
                ('time_start', models.DateTimeField(default=django.utils.timezone.now)),
                ('time_end', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.CharField(choices=[('manual', 'manual'), ('file', 'file'), ('somax', 'somax'), ('auto', 'auto')], default='manual', max_length=100)),
                ('created_by', models.ForeignKey(db_column='created_by', default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(blank=True, db_column='document', null=True, on_delete=django.db.models.deletion.CASCADE, to='WorkConfig.Documents', to_field='name')),
                ('name', models.ForeignKey(db_column='name', on_delete=django.db.models.deletion.CASCADE, to='WorkConfig.Workers', to_field='name', verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='WorkerScheduled',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('duration_actual', models.DurationField(default=datetime.timedelta(0))),
                ('time_start', models.DateTimeField(default=django.utils.timezone.now)),
                ('time_end', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.CharField(choices=[('manual', 'manual'), ('file', 'file'), ('somax', 'somax'), ('auto', 'auto')], default='manual', max_length=100)),
                ('current_status', models.CharField(choices=[('Working', 'Working'), ('Canceled', 'Canceled'), ('Complete', 'Complete'), ('Uncomplete', 'Uncomplete')], default='Working', max_length=100)),
                ('available_id', models.ForeignKey(db_column='available_id', on_delete=django.db.models.deletion.CASCADE, to='WorkWorkers.WorkerAvailable')),
                ('created_by', models.ForeignKey(db_column='created_by', default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(blank=True, db_column='document', null=True, on_delete=django.db.models.deletion.CASCADE, to='WorkConfig.Documents', to_field='name')),
                ('name', models.ForeignKey(db_column='name', on_delete=django.db.models.deletion.CASCADE, to='WorkConfig.Workers', to_field='name')),
                ('task_id', models.ForeignKey(db_column='task_id', on_delete=django.db.models.deletion.CASCADE, to='WorkTasks.Tasks')),
            ],
        ),
    ]
