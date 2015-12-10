# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'hipchat.views',
    url(r'^descriptor/(?P<app_id>\d+)/$', 'descriptor', name="descriptor"),
    url(r'^callback/(?P<app_id>\d+)/$', 'install', name="install"),
    url(r'^callback/(?P<app_id>\d+)/(?P<oauth_id>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})$',
        'delete', name="delete"),
)
