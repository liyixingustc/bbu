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