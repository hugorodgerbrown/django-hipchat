# -*- coding: utf-8 -*-
"""hipchat models.

https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

"""
import datetime
from urlparse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.timezone import now as tz_now

USE_SSL = getattr(settings, 'USE_SSL', True)


def get_full_url(path):
    """Return the full URL (scheme, domain, path) for a relative path."""
    scheme = "https://" if USE_SSL else "http://"
    domain = Site.objects.get_current().domain
    return urljoin(scheme + domain, path)


class Scope(models.Model):

    """HipChat API scope.

    Scopes are taken from the API documentation. They are stored in a model
    so that we can have a many-to-many relationship with the app.

    https://ecosystem.atlassian.net/wiki/display/HIPDEV/API+scopes

    """
    name = models.CharField(
        max_length=25,
        help_text="The name of the scope as required by HipChat."
    )
    description = models.CharField(
        max_length=100,
        help_text="The capabilities allowed within this scope."
    )
    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<ApiScope id=%s name='%s'>" % (self.id, self.name)

    def save(self, *args, **kwargs):
        super(HipChatApp, self).save(*args, **kwargs)
        return self


class HipChatApp(models.Model):

    """Store the data required for the HipChat add-on."""

    key = models.CharField(
        max_length=100,
        help_text="Has to be unique",
        unique=True
    )
    name = models.CharField(
        max_length=100,
        help_text=(
            "Name of your add-on, will be shown to users "
            "when they install your integration."
        )
    )
    description = models.CharField(
        max_length=200,
        help_text=(
            "Description of your add-on, will be shown to "
            "users when they install your integration."
        ),
        blank=True
    )
    vendor_name = models.CharField(
        max_length=100,
        help_text=(
            "Name of your company (will be shown to users "
            "when they install your integration)."
        )
    )
    vendor_url = models.URLField(
        help_text=(
            "Company website (will be shown to users when "
            "they install you integration)."
        )
    )
    scopes = models.ManyToManyField(
        Scope,
        help_text=(
            "List of security scopes you need, which will "
            "dictate what REST APIs your add-on can call."
        )
    )
    allow_global = models.BooleanField(
        default=False,
        help_text=(
            "Set to True if your addon can be installed globally "
            "(which makes it accessible in all rooms)."
        )
    )
    allow_room = models.BooleanField(
        default=False,
        help_text=("Set to true if your addon can be installed in a room.")
    )

    def __unicode__(self):
        return self.key

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<HipChatApp id=%s key='%s'>" % (self.id, self.key)

    @property
    def descriptor_url(self):
        """Format the fully-qualified URL for the descriptor."""
        return get_full_url(reverse('hipchat:descriptor', kwargs={'app_id': self.id}))

    @property
    def install_url(self):
        """Format the fully-qualified URL for the descriptor."""
        return get_full_url(reverse('hipchat:install', kwargs={'app_id': self.id}))

    @property
    def scopes_list(self):
        """Return related scopes as a comma-separated string."""
        return [s.name for s in self.scopes.all()]

    @property
    def descriptor(self):
        """Return the object formatted as the HipChat add-on descriptor."""
        descriptor = {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "vendor": {
                "name": self.vendor_name,
                "url": self.vendor_url
            },
            "links": {
                "self": self.descriptor_url,
            },
            "capabilities": {
                "hipchatApiConsumer": {
                    "scopes": self.scopes_list
                },
                "installable": {
                    "callbackUrl": self.install_url,
                    "allowGlobal": self.allow_global,
                    "allowRoom": self.allow_room
                },
            }
        }
        return descriptor

    def save(self, *args, **kwargs):
        super(HipChatApp, self).save(*args, **kwargs)
        return self


class AppInstallQuerySet(models.query.QuerySet):

    """Custom AppInstall QuerySet."""

    def create_from_install(self, app, json_data):
        """Create a new AccessData object from JSON data.

        This method handles the JSON posted back from the install.
        https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

        NB this will fail hard if the JSON is incorrectly formatted - this is
        by design.

        Args:
            app: HipChatApp that this install relates to
            json_data: a dict, the HipChat callback request POST contents.

        """
        install = AppInstall(app=app)
        install.oauth_id = json_data['oauthId']
        install.oauth_secret = json_data['oauthSecret']
        install.group_id = json_data['groupId']
        if 'roomId' in json_data:
            install.room_id = json_data['roomId']
        # this will raise IntegrityError if the oauth_id is a duplicate
        return install.save()


class AppInstall(models.Model):

    """Store data returned from the HipChat API re. an app install.

    Specific information required for access rights - see
    https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

    Returned from the initial install callback:

        {
             "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
             "oauthId": "abc",
             "oauthSecret": "xyz",
             "groupId": 123,
             "roomId": "1234"
        }

    The capabilitiesUrl returns a JSON document containing all the URLs used to
    interact with the API. One of these is the `tokenUrl` - which is used in
    conjunction with the oauth creds returned in the callback to generate an
    API access token:

        { 
          access_token: '5236346233724572457245gdgreyt345yreg',
          expires_in: 431999999,
          group_id: 123,
          group_name: 'Example Company',
          scope: 'send_notification',
          token_type: 'bearer' 
        }

    """
    app = models.ForeignKey(
        HipChatApp,
        help_text="App to which this access info belongs."
    )
    # the following attrs are set by the install postback from HipChat
    oauth_id = models.CharField(
        max_length=20,
        help_text="OAuth ID returned from the app install postback.",
        unique=True
    )
    oauth_secret = models.CharField(
        max_length=20,
        help_text="OAuth secret returned from the app install postback."
    )
    group_id = models.IntegerField(
        blank=True,
        help_text="Name of the group, returned from the token URL."
    )
    room_id = models.IntegerField(
        blank=True, null=True,
        help_text="Id of the room into which the app was installed."
    )
    # the following attrs are set by posting to the token_url
    access_token = models.CharField(
        max_length=40,
        help_text="API access token",
        blank=True
    )
    expires_at = models.DateTimeField(
        blank=True, null=True,
        help_text="The datetime at which this access_token will expire."
    )
    scope = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma separated list of scopes."
    )
    installed_at = models.DateTimeField(
        help_text="Timestamp set when the app is installed."
    )

    objects = AppInstallQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.installed_at = self.installed_at or tz_now()
        super(AppInstall, self).save(*args, **kwargs)
        return self

    @property
    def has_expired(self):
        """Return True if the token is passed its expires_at datetime."""
        return self.expires_at < tz_now()

    @property
    def http_auth(self):
        """Return HTTPBasicAuth object using oauth_id, secret."""
        return HTTPBasicAuth(self.oauth_id, self.oauth_secret)

    def refresh_access_token(self):
        """Fetch a new access_token from HipChat for this install.

        This method is used to fill in the second half of the app install
        properties - including the access_token, which is the token used
        when calling the HipChat API.

        """
        url = "https://api.hipchat.com/v2/oauth/token"
        data = {'grant_type': 'client_credentials', 'scope': self.app.scopes_list}
        resp = requests.post(url, auth=self.http_auth, data=data)
        data = resp.json()
        self.access_token = data['access_token']
        self.group_id = data['group_id']
        self.group_name = data['group_name']
        self.scope = data['scope']
        if 'roomId' in data:
            self.room_id = data['roomId']
        self.expires_at = tz_now() + datetime.timedelta(seconds=data['expires_in'])
        return self.save()
