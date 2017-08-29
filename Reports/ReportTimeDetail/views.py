from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect,csrf_exempt
import pandas as pd
from utils.mapper import mapper
from .viewsManager import PageManager
# Create your views here.
# from .utils.LoadConfigData import LoadConfigData

class Page:

    @staticmethod
    @staff_member_required(login_url='/login/')
    @csrf_protect
    def index(request, *args, **kwargs):
        template_name = 'ReportLostTimeDetail/{page}.html'.format(page=kwargs['page'])
        # LoadConfigData().load()
        return render(request, template_name)

    class Panel:
        class Form:

            @staticmethod
            def submit(request, *args, **kwargs):
                response = PageManager.PanelManager.FormManager.submit(request, *args, **kwargs)
                return response


mapping = pd.DataFrame([
    {'page': 'ReportLostTimeDetail', 'panel': 'None', 'widget': 'None', 'func': 'index', 'register': Page.index},
    {'page': 'ReportLostTimeDetail', 'panel': 'Panel1', 'widget': 'Form1', 'func': 'Submit', 'register': Page.Panel.Form.submit},
])


@csrf_protect
def as_view(request, *args, **kwargs):
    page = kwargs.get('page')
    panel = kwargs.get('panel')
    widget = kwargs.get('widget')
    func = kwargs.get('func')
    register = mapper(mapping, page, panel, widget, func)
    response = register(request, *args, **kwargs)

    return response


