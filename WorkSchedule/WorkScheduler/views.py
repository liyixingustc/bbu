from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
import pandas as pd
from utils.mapper import mapper
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
            def create(self, request, *args, **kwargs):
                pass


mapping = pd.DataFrame([
    {'page': 'WorkScheduler', 'panel': 'None', 'widget': 'None', 'func': 'index', 'register': Page.index},
    {'page': 'WorkScheduler', 'panel': 'Panel1', 'widget': 'TimeLine1', 'func': 'create', 'register': Page.Panel.TimeLine.create},
])


def as_view(request, *args, **kwargs):
    page = kwargs.get('page')
    panel = kwargs.get('panel')
    widget = kwargs.get('widget')
    func = kwargs.get('func')

    register = mapper(mapping, page, panel, widget, func)
    response = register(request, *args, **kwargs)

    return response


