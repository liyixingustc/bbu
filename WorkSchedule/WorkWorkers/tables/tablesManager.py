import os
import pandas as pd
from datetime import datetime as dt,timedelta
import pytz
from django.shortcuts import HttpResponse
from django.http import JsonResponse

from ..models.models import *
from ...WorkConfig.models import *

from utils.TableConventor import TableConvertor


class WorkWorkersPanel1Table1Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls):

        workers = Workers.objects.all().values_list('name', 'company')
        num = workers.count()
        worker_data=workers
        if worker_data.exists():
            worker_data = pd.DataFrame.from_records(worker_data.values('id', 'name', 'company'))
            worker_data = worker_data.to_dict(orient='records')
            response = {
                'total': num,
                'rows': worker_data
            }
        else:
            worker_data = []
            response = {
                'total': 0,
                'rows': []
            }

        return JsonResponse(response,safe=False)


    @classmethod
    def add_data(cls, parameters):
        #name, last_name, first_name, company, level, shirt, status, type, somax_account
        name = str(parameters['name'])
        last_name = str(parameters['last_name'])
        first_name = str(parameters['first_name'])
        companyname = str(parameters['company'])
        company = Company.objects.get(business_name=companyname)
        level = str(parameters['level'])
        shift = str(parameters['shift'])
        status = str(parameters['status'])
        type = str(parameters['type'])
        worker = Workers.objects.create(name = name, last_name = last_name, first_name = first_name, company = company, level = level, shift = shift, status = status, type = type)
        return


    @classmethod
    def edit(cls, parameters):

        date = dt.strptime(parameters['date'].split('<br>')[0],'%Y-%m-%d').date()
        duration = timedelta(hours=float(parameters['duration']))

        name = Workers.objects.get(name= parameters['name'])
        WorkerAvailable.objects.update_or_create(name=name,date=date,
                                                 defaults={'duration':duration})

        return


    @classmethod
    def get_companys(cls):
        companys = Company.objects.all().values_list('business_name')
        if companys.exists():
            companys = pd.DataFrame.from_records(companys.values('business_name'))
            companys = companys.to_dict(orient='records')
            return JsonResponse(companys,safe=False)
        return JsonResponse({})


    @classmethod
    def delete_data(cls, parameters):
        parameterstr = str(parameters['ids'])
        parameterlist = parameterstr.split(',')
        for parameter in parameterlist:
            parameterno = int(parameter)
            print(parameterno)
            #WorkerAvailable.objects.filter(name=parameter).delete()
            worker = Workers.objects.get(id=parameterno)
            worker.delete()
            #WorkerAvailable.objects.update_or_create(name=name,date=date,defaults={'duration':duration})

        return




class WorkWorkersPanel1Table2Manager:

    now = dt.now(tz=pytz.timezone('America/New_York'))

    @classmethod
    def set_data(cls, parameters):

        period_start = dt.strptime(parameters['period_start'], '%Y-%m-%d')
        period_end = dt.strptime(parameters['period_end'], '%Y-%m-%d')

        tasks = WorkerScheduledTask.objects.filter(task_id__period_start__exact=period_start,
                                                   task_id__period_end__exact=period_end,
                                                   workerscheduled_id__name__name__exact=parameters['name'],
                                                   workerscheduled_id__date__range=[period_start, period_end])\
            .values('task_id__line',
                    'task_id__working_order',
                    'task_id__description',
                    'task_id__working_type',
                    'task_id__priority',
                    'workerscheduled_id__date',
                    'workerscheduled_id__duration')

        tasks = pd.DataFrame.from_records(tasks, columns=['task_id__line',
                                                          'task_id__working_order',
                                                          'task_id__description',
                                                          'task_id__working_type',
                                                          'task_id__priority',
                                                          'workerscheduled_id__date',
                                                          'workerscheduled_id__duration'])

        tasks.rename_axis({'task_id__line': 'line',
                           'task_id__working_order': 'order',
                           'task_id__description': 'description',
                           'task_id__working_type': 'type',
                           'task_id__priority': 'priority',
                           'workerscheduled_id__date': 'date',
                           'workerscheduled_id__duration': 'scheduled',
                           },
                          axis=1, inplace=True)

        tasks['scheduled'] = tasks['scheduled'].apply(lambda x: x.total_seconds()/3600)
        tasks['date'] = tasks['date'].apply(lambda x: str(x))

        data = tasks

        return data
