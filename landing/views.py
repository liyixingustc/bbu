from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import auth

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import SignUpForm, LoginForm
from accounts.models import User

# Create your views here.


@api_view(['GET', 'POST'])
def login(request):

    if request.method == 'POST':
        form = LoginForm(request.data)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data['remember']

            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    # Redirect to a success page.
                    return Response({'status':1,'message':'OK', 'url': 'WorkSchedule/1/WorkConfig/index'})
                else:
                    # Return a 'disabled account' error message
                    return Response({'status':0,'message':'Disabled account'})
            else:
                # Return an 'invalid login' error message.
                return Response({'status': 0, 'message': 'Wrong username or password format'})
        else:
            return Response({'status': 0,'message':'Wrong username or password'})

    return render(request,'landing/login.html')


@csrf_protect
def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # get form data and insert into the database

            user=User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                company=form.cleaned_data['company']
            )
            return JsonResponse({'status':1,'message':'Register Success!'})
        else:

            return JsonResponse({'status':1,'message':form.errors})
    else:
        pass
    return render(request,'landing/signup.html')

def logout(request):
    auth.logout(request)
    return redirect('/')