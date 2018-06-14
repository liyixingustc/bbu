from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect

from .tables.tables import *
from .tables.tablesManager import *

from datetime import datetime as dt

# Create your views here.


class Page:

    @classmethod
    def as_view(cls, request, *args, **kwargs):
        page = kwargs.get('page')
        panel = kwargs.get('panel')
        widget = kwargs.get('widget')
        func = kwargs.get('func')

        if widget:
            if 'Form' in widget:
                if func == 'Submit':
                    return cls.Panel.Form.submit(request, *args, **kwargs)
            if 'Table' in widget:
                if func == 'Create':
                    return cls.Panel.Table.create(request, *args, **kwargs)
                if func == 'Edit':
                    return cls.Panel.Table.edit(request, *args, **kwargs)
        elif panel:
            pass
        elif page:
            if func == 'index':
                return cls.index(request, *args, **kwargs)

    @staticmethod
    @staff_member_required(login_url='/login/')
    @csrf_protect
    def index(request, *args, **kwargs):

        template_name = 'WorkWorkers/{page}.html'.format(page=kwargs['page'])

        return render(request, template_name)

    class Panel:

        class Form:

            @staticmethod
            def submit(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkWorkers':
                    if panel == 'Panel1':
                        if widget == 'Form1':
                            if func == 'Submit':
                                pass

                return JsonResponse({'a': 1})

        class Table:

            @staticmethod
            def create(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkWorkers':
                    if panel == 'Panel1':
                        if widget == 'Table1':
                            if func == 'Create':
                                period_start = request.GET.get('PeriodStart')
                                period_end = request.GET.get('PeriodEnd')

                                data = WorkWorkersPanel1Table1Manager.set_data(period_start, period_end)
                                return data

                        elif widget == 'Table2':
                            if func == 'Create':
                                parameters = {}
                                parameters['period_start'] = request.POST.get('start')
                                parameters['period_end'] = request.POST.get('end')
                                parameters['name'] = request.POST.get('row[name]')
                                parameters['date'] = request.POST.get('row[date]')

                                tables_template_name = 'WorkWorkers/WorkWorkers_Panel1_Table2.html'
                                data = WorkWorkersPanel1Table2Manager.set_data(parameters)

                                return data

                return JsonResponse({})

            @staticmethod
            def edit(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkWorkers':
                    if panel == 'Panel1':
                        if widget == 'Table1':
                            if func == 'Edit':
                                parameters = {}
                                parameters['name'] = request.POST.get('name')
                                parameters['duration'] = request.POST.get('duration')
                                parameters['date'] = request.POST.get('date')

                                WorkWorkersPanel1Table1Manager.edit(parameters)
                                return JsonResponse({})

                return JsonResponse({})
