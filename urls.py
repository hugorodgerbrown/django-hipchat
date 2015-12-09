# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.contrib import admin  # , staticfiles

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hipchat/', include('hipchat.urls', namespace="hipchat")),
    # url(r'^static/(?P<path>.*)$', staticfiles.views.serve),
)
