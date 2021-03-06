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
        template_name = 'WorkScheduler/{page}.html'.format(page=kwargs['page'])
        return render(request, template_name)

    class Panel:
        class TimeLine:
            @staticmethod
            def resources(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.resources(request, *args, **kwargs)
                return response

            @staticmethod
            def events(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.events(request, *args, **kwargs)
                return response

            @staticmethod
            def event_update(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.event_update(request, *args, **kwargs)
                return response

            @staticmethod
            def event_create(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.event_create(request, *args, **kwargs)
                return response

            @staticmethod
            def syc_tasks_from_somax(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.syc_tasks_from_somax(request, *args, **kwargs)
                return response

            @staticmethod
            def syc_tasks_to_somax(request, *args, **kwargs):
                response = PageManager.PanelManager.TimeLineManager.syc_tasks_to_somax(request, *args, **kwargs)
                return response

        class Modal:
            @staticmethod
            def select_submit(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.select_submit(request, *args, **kwargs)
                return response

            @staticmethod
            def tasks_submit(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.tasks_submit(request, *args, **kwargs)
                return response

            @staticmethod
            def add_worker_submit(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.add_worker_submit(request, *args, **kwargs)
                return response

            @staticmethod
            def add_worker_workers(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.add_worker_workers(request, *args, **kwargs)
                return response

            @staticmethod
            def worker_submit(request, *args, **kwargs):
                response = PageManager.PanelManager.ModalManager.worker_submit(request, *args, **kwargs)
                return response

        class Table:
            @staticmethod
            def create(request, *args, **kwargs):
                response = PageManager.PanelManager.TableManager.create(request, *args, **kwargs)
                return response

            @staticmethod
            def edit(request, *args, **kwargs):
                response = PageManager.PanelManager.TableManager.edit(request, *args, **kwargs)
                return response

        class KPIBoard:
            @staticmethod
            def update(request, *args, **kwargs):
                response = PageManager.PanelManager.KPIBoardManager.update(request, *args, **kwargs)
                return response

        class Form:
            @staticmethod
            def submit(request, *args, **kwargs):
                response = PageManager.PanelManager.FormManager.submit(request, *args, **kwargs)
                return response


mapping = pd.DataFrame([
    {'page': 'WorkScheduler', 'panel': 'None', 'widget': 'None', 'func': 'index', 'register': Page.index},

    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'resources', 'register': Page.Panel.TimeLine.resources},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'events', 'register': Page.Panel.TimeLine.events},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'event_update', 'register': Page.Panel.TimeLine.event_update},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'event_create', 'register': Page.Panel.TimeLine.event_create},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'syc_tasks_from_somax', 'register': Page.Panel.TimeLine.syc_tasks_from_somax},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'syc_tasks_to_somax', 'register': Page.Panel.TimeLine.syc_tasks_to_somax},

    {'page': 'WorkScheduler', 'panel': 'Panel2', 'widget': 'Table1', 'func': 'create', 'register': Page.Panel.Table.create},
    {'page': 'WorkScheduler', 'panel': 'Panel2', 'widget': 'Table1', 'func': 'edit', 'register': Page.Panel.Table.edit},

    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'Modal1', 'func': 'select_submit', 'register': Page.Panel.Modal.select_submit},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'Modal2', 'func': 'tasks_submit', 'register': Page.Panel.Modal.tasks_submit},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'Modal3', 'func': 'add_worker_submit', 'register': Page.Panel.Modal.add_worker_submit},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'Modal3', 'func': 'add_worker_workers', 'register': Page.Panel.Modal.add_worker_workers},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'Modal4', 'func': 'worker_submit', 'register': Page.Panel.Modal.worker_submit},

    {'page': 'WorkScheduler', 'panel': 'Panel3', 'widget': 'KPIBoard', 'func': 'update', 'register': Page.Panel.KPIBoard.update},

    {'page': 'WorkScheduler', 'panel': 'Panel4', 'widget': 'Form1', 'func': 'Submit', 'register': Page.Panel.Form.submit},
])


def as_view(request, *args, **kwargs):
    page = kwargs.get('page')
    panel = kwargs.get('panel')
    widget = kwargs.get('widget')
    func = kwargs.get('func')

    register = mapper(mapping, page, panel, widget, func)
    response = register(request, *args, **kwargs)

    return response

