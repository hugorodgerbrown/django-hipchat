# -*- coding: utf-8 -*-
import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from hipchat.models import HipChatApp, AppInstall,  AccessToken, Glance


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


def get_access_tokens(modeladmin, request, queryset):
    """Refresh API access tokens for selected installs."""
    for obj in queryset:
        obj.get_access_token()

get_access_tokens.short_description = "Get access tokens for selected installs."

class AppInstallAdmin(admin.ModelAdmin):

    """Admin model of AppInstall objects."""

    list_display = (
        'app',
        'group_id',
        'room_id',
    )
    readonly_fields = (
        'app',
        'oauth_id',
        'oauth_secret',
        'group_id',
        'room_id',
        'installed_at'
    )
    actions = (get_access_tokens,)


class AccessTokenAdmin(admin.ModelAdmin):

    """Admin model of AccessToken objects."""

    list_display = (
        'app',
        'install',
        'access_token',
        'group_name',
        'scope',
        'expires_at',
        'has_expired'
    )
    readonly_fields = (
        'app',
        'install',
        'group_id',
        'group_name',
        'access_token',
        'expires_at',
        'created_at',
        'scope',
    )


class GlanceAdmin(admin.ModelAdmin):

    """Admin model of Glance objects."""

    list_display = (
        'app',
        'key',
        'name',
    )


admin.site.register(HipChatApp, HipChatAppAdmin)
admin.site.register(AppInstall, AppInstallAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(Glance, GlanceAdmin)
