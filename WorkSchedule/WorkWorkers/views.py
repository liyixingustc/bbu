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
                if func == 'Get_Company':
                    return cls.Panel.Form.get_company(request, *args, **kwargs)
            if 'Table' in widget:
                if func == 'Create':
                    return cls.Panel.Table.create(request, *args, **kwargs)
                if func == 'Edit':
                    return cls.Panel.Table.edit(request, *args, **kwargs)
                if func == 'Delete':
                    return cls.Panel.Table.delete(request, *args, **kwargs)
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
                                #name, last_name, first_name, company, level, shirt, status, type, somax_account
                                for key in request.POST:
                                    print(key)
                                    value = request.POST[key]
                                    print(value)
                                parameters = {}
                                parameters['name'] = request.POST.get('name')
                                parameters['last_name'] = request.POST.get('last_name')
                                parameters['first_name'] = request.POST.get('first_name')
                                parameters['company'] = request.POST.get('company')
                                parameters['level'] = request.POST.get('level')
                                parameters['shift'] = request.POST.get('shift')
                                parameters['status'] = request.POST.get('status')
                                parameters['type'] = request.POST.get('type')
                                print(parameters)
                                WorkWorkersPanel1Table1Manager.add_data(parameters)
                                return JsonResponse({})

                return JsonResponse({})


            @staticmethod
            def get_company(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkWorkers':
                    if panel == 'Panel1':
                        if widget == 'Form1':
                            if func == 'Get_Company':
                                #name, last_name, first_name, company, level, shirt, status, type, somax_account
                                companyslist = WorkWorkersPanel1Table1Manager.get_companys()
                                print(companyslist)
                                return companyslist

                return JsonResponse({})

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
                                data = WorkWorkersPanel1Table1Manager.set_data()
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


            @staticmethod
            def delete(request, *args, **kwargs):

                page = kwargs['page']
                panel = kwargs['panel']
                widget = kwargs['widget']
                func = kwargs['func']

                if page == 'WorkWorkers':
                    if panel == 'Panel1':
                        if widget == 'Table1':
                            if func == 'Delete':
                                parameters = {}
                                parameters['ids'] = request.POST.get('ids')
                                data = WorkWorkersPanel1Table1Manager.delete_data(parameters)
                                return JsonResponse({})

                return JsonResponse({})
