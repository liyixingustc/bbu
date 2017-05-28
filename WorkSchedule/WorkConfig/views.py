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
def index(request, *args, **kwargs):

    template_name = 'WorkConfig/{page}.html'.format(page=kwargs['page'])

    return render(request, template_name)


class Panel:

    class Form:

        @classmethod
        def submit(cls,request,*args,**kwargs):

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
