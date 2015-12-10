# -*- coding: utf-8 -*-
import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from hipchat.models import HipChatApp, AppInstall


class HipChatAppAdmin(admin.ModelAdmin):

    """Admin model for HipChatApp objects."""

    list_display = (
        'key',
        'name',
        'description',
        'allow_global',
        'allow_room'
    )
    readonly_fields = ('app_descriptor',)

    def app_descriptor(self, obj):
        """Return formatted JSON."""
        pretty = json.dumps(
            obj.descriptor,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        return mark_safe("<code>%s</code>" % pretty.replace(" ", "&nbsp;"))


def refresh_access_tokens(modeladmin, request, queryset):
    """Refresh API access tokens for selected installs."""
    for obj in queryset:
        obj.refresh_access_token()
refresh_access_tokens.short_description = "Refresh selected app install access tokens."

class AppInstallAdmin(admin.ModelAdmin):

    """Admin model of AppInstall objects."""

    list_display = (
        'app',
        'oauth_id',
        'group_id',
        'room_id',
        'expires_at',
        'installed_at',
        'has_expired'
    )
    readonly_fields = (
        'app',
        'oauth_id',
        'oauth_secret',
        'group_id',
        'access_token',
        'room_id',
        'expires_at',
        'scope',
        'installed_at'
    )
    actions = (refresh_access_tokens,)


admin.site.register(HipChatApp, HipChatAppAdmin)
admin.site.register(AppInstall, AppInstallAdmin)
