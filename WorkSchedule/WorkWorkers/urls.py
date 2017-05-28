from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/(?P<func>\w+)$',
        views.Page.as_view, name='WorkWorkers_Page'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<func>\w+)/$',
        views.Page.as_view, name='WorkWorkers_Panel'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.Page.as_view, name='WorkWorkers_Widget'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.Page.as_view, name='WorkWorkers_Func'),
]