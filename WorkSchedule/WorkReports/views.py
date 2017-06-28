from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
import pandas as pd
from utils.mapper import mapper
from .viewsManager import PageManager
# Create your views here.


class Page:

    @staticmethod
    @staff_member_required(login_url='/login/')
    @csrf_protect
    def index(request, *args, **kwargs):
        template_name = 'WorkReports/{page}.html'.format(page=kwargs['page'])
        return render(request, template_name)

    class Panel:

        class Modal:
            @staticmethod
            def extend_worker_avail(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.extend_worker_avail(request, *args, **kwargs)
                return response

        class Table:
            @staticmethod
            def create(request, *args, **kwargs):
                response = PageManager.PanelManager.TableManager.create(request, *args, **kwargs)
                return response

        class Form:
            @staticmethod
            def submit(request, *args, **kwargs):
                response = PageManager.PanelManager.FormManager.submit(request, *args, **kwargs)
                return response

            @staticmethod
            def download(request, *args, **kwargs):
                response = PageManager.PanelManager.FormManager.download(request, *args, **kwargs)
                return response


mapping = pd.DataFrame([
    {'page': 'WorkReports', 'panel': 'None', 'widget': 'None', 'func': 'index', 'register': Page.index},
    {'page': 'WorkReports', 'panel': 'Panel1', 'widget': 'Table1', 'func': 'create', 'register': Page.Panel.Table.create},
    {'page': 'WorkReports', 'panel': 'Panel1', 'widget': 'Form1', 'func': 'submit', 'register': Page.Panel.Form.submit},
    {'page': 'WorkReports', 'panel': 'Panel1', 'widget': 'Form1', 'func': 'download', 'register': Page.Panel.Form.download},
])


def as_view(request, *args, **kwargs):
    page = kwargs.get('page')
    panel = kwargs.get('panel')
    widget = kwargs.get('widget')
    func = kwargs.get('func')

    register = mapper(mapping, page, panel, widget, func)
    response = register(request, *args, **kwargs)

    return response

