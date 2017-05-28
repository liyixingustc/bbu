from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect

from .tables.tables import *
from .tables.tablesManager import *

from datetime import datetime as dt

# Create your views here.


@staff_member_required(login_url='/login/')
@csrf_protect
def index(request,*args,**kwargs):

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

            if page == 'WorkConfig':
                if panel == 'Panel1':
                    if widget == 'Form1':
                        if func == 'Submit':
                            pass

            return JsonResponse({})

    class Table:

        @classmethod
        def create(cls, request, *args, **kwargs):

            page = request.GET.get('page')
            panel = request.GET.get('panel')
            widget = request.GET.get('widget')
            func = request.GET.get('func')

            if page == 'WorkConfig':
                if panel == 'Panel1':
                    if widget == 'Form1':
                        if func == 'Submit':
                            pass

    @classmethod
    def request_inits(cls, request):

        page = request.GET.get('page')
        panel = request.GET.get('panel')
        widget = request.GET.get('widget')
        func = request.GET.get('func')

        return {'page':page,'panel':panel,'widget':widget,'func':func}
