from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/$', views.index, name='report'),
    url(r'^(?P<page>\w+)/table/create_table/$', views.table.create_table),
    url(r'^IngestorCheck/UpdateData/', views.UpdateData),
    url(r'^(?P<page>\w+)/(?P<app>\w+)/download/$', views.download),
]