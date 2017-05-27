from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/$', views.index, name='WorkTasks'),
]