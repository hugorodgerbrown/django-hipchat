# -*- coding: utf-8 -*-
from django.contrib import admin

from hipchat.models import HipChatApp


class HipChatAppAdmin(admin.ModelAdmin):

    """Admin model for HipChatApp objects."""

    list_display = (
        'key',
        'name',
        'description',
        'allow_global',
        'allow_room'
    )

admin.site.register(HipChatApp, HipChatAppAdmin)
