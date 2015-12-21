# -*- coding: utf-8 -*-
import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from hipchat.models import Addon, Install, Glance, GlanceUpdate


class DescriptorMixin(object):

    """Provides access to pretty-formatted version of descriptor property."""

    def pretty_descriptor(self, obj):
        """Return pretty formatted version of descriptor() output."""
        try:
            pretty = json.dumps(
                obj.descriptor(),
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
            return mark_safe("<code>%s</code>" % pretty.replace(" ", "&nbsp;"))
        except Exception as ex:
            print(ex)

    pretty_descriptor.short_description = "Descriptor (formatted)"


class GlanceInline(admin.StackedInline):

    """Inline admin for viewing / adding Addon glances."""

    model = Glance
    show_change_link = True
    min_num = 0
    max_num = 1


class AddonAdmin(DescriptorMixin, admin.ModelAdmin):

    """Admin model for Addon objects."""

    list_display = (
        'key',
        'name',
        'description',
        'allow_global',
        'allow_room',
        'install_link'
    )
    readonly_fields = ('pretty_descriptor',)
    inlines = (GlanceInline,)

    def install_link(self, obj):
        """Return link to install direct."""
        return (
            "<a target='_blank' "
            "href='https://www.hipchat.com/addons/install?url=%s'>Install</a>"
            % obj.descriptor_url()
        )
    install_link.allow_tags = True
    install_link.short_description = "Click to install"


def get_access_tokens(modeladmin, request, queryset):
    """Refresh API access tokens for selected installs."""
    for obj in queryset:
        obj.get_access_token()

get_access_tokens.short_description = "Get access tokens for selected installs."


class InstallAdmin(admin.ModelAdmin):

    """Admin model of Install objects."""

    list_display = (
        'app',
        'group_id',
        'room_id',
        'oauth_short'
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

    def oauth_short(self, obj):
        return obj.oauth_id[:8]
    oauth_short.short_description = "OAuth Id (truncated)"


class GlanceAdmin(DescriptorMixin, admin.ModelAdmin):

    """Admin model of Glance objects."""

    list_display = (
        'app',
        'key',
        'name',
        'target'
    )
    readonly_fields = ('pretty_descriptor',)


class GlanceUpdateAdmin(admin.ModelAdmin):

    """Admin model of Glance objects."""

    list_display = (
        'glance',
        'label',
        'lozenge',
        'icon'
    )

    def lozenge(self, obj):
        if obj.has_lozenge:
            return u"(%s) %s" % (obj.lozenge_type, obj.lozenge_value)
        else:
            return None

    def icon(self, obj):
        """Display the icon in the list view."""
        if obj.has_icon:
            return mark_safe("<img src='%s'>" % obj.icon_url)
        else:
            return None


admin.site.register(Addon, AddonAdmin)
admin.site.register(Install, InstallAdmin)
admin.site.register(Glance, GlanceAdmin)
admin.site.register(GlanceUpdate, GlanceUpdateAdmin)
