from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/(?P<func>\w+)$',
        views.as_view, name='ReportTimeDetail_Page'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportTimeDetail_Panel'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportTimeDetail_Widget'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportTimeDetail_Func'),
]