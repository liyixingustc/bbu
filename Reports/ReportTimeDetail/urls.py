from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/(?P<func>\w+)$',
        views.as_view, name='ReportLostTimeDetail_Page'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportLostTimeDetail_Panel'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportLostTimeDetail_Widget'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.as_view, name='ReportLostTimeDetail_Func'),
]