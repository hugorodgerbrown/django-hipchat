# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'hipchat.views',
    url(r'^descriptor/(?P<app_id>\d+)/$', 'descriptor', name="descriptor"),
    url(r'^install/(?P<app_id>\d+)/$', 'install', name="install"),
)
