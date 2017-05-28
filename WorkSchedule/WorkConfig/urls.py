from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<page>\w+)/$', views.index, name='WorkConfig'),
    # url(r'^(?P<page>\w+)/(?P<panel>\w+)/$', views.index, name='WorkConfig_Panel'),
    # url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/$', views.index, name='WorkConfig_Widget'),
    url(r'^(?P<page>\w+)/(?P<panel>\w+)/(?P<widget>\w+)/(?P<func>\w+)/$',
        views.Panel.Form.submit, name='WorkConfig_Func'),

]