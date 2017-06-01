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

        template_name = 'WorkTasks/{page}.html'.format(page=kwargs['page'])

        return render(request, template_name)

    class Panel:

        class Form:

            @staticmethod
            def submit(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkTasks':
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

                if page == 'WorkTasks':
                    if panel == 'Panel1':
                        if widget == 'Table1':
                            if func == 'Create':
                                period_start = request.GET.get('PeriodStart')
                                period_end = request.GET.get('PeriodEnd')

                                tables_template_name = 'WorkTasks/WorkTasks_Panel1_Table1.html'
                                data = WorkTasksPanel1Table1Manager.set_data(period_start, period_end)
                                table = WorkTasksPanel1Table1(data)
                                return render(request, tables_template_name, {'table': table})
                        elif widget == 'Table2':
                            if func == 'Create':
                                parameters = {}
                                parameters['period_start'] = request.POST.get('start')
                                parameters['period_end'] = request.POST.get('end')
                                parameters['working_order'] = request.POST.get('row[working_order]')

                                tables_template_name = 'WorkTasks/WorkTasks_Panel1_Table2.html'

                                data2a = WorkTasksPanel1Table2aManager.set_data(parameters)
                                table2a = WorkTasksPanel1Table2a(data2a)

                                data2b = WorkTasksPanel1Table2bManager.set_data(parameters)
                                table2b = WorkTasksPanel1Table2b(data2b)

                                return render(request, tables_template_name, {'table2a': table2a,
                                                                              'table2b': table2b})

                return JsonResponse({})

            @staticmethod
            def edit(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkTasks':
                    if panel == 'Panel1':
                        if widget == 'Table2a':
                            if func == 'Edit':
                                parameters = {}
                                parameters['name'] = request.POST.get('name')
                                parameters['duration'] = request.POST.get('duration')
                                parameters['date'] = request.POST.get('date')

                                WorkTasksPanel1Table2aManager.edit(parameters)
                                return JsonResponse({})
                        elif widget == 'Table2b':
                            if func == 'Edit':
                                parameters = {}
                                parameters['name'] = request.POST.get('name')
                                parameters['duration'] = request.POST.get('duration')
                                parameters['date'] = request.POST.get('date')

                                WorkTasksPanel1Table2bManager.edit(parameters)
                                return JsonResponse({})

                return JsonResponse({})
