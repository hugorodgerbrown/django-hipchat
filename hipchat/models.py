# -*- coding: utf-8 -*-
"""hipchat models.

https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

"""
import datetime
import logging
from urlparse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.timezone import now as tz_now

SCHEME = "https://" if getattr(settings, 'USE_SSL', True) else "http://"

logger = logging.getLogger(__name__)


def get_domain():
    """Return the current domain as specified in the Sites app.

    This has been pulled out into a function to make it easy to mock
    out in tests.

    """
    return Site.objects.get_current().domain


def get_full_url(path):
    """Return the full URL (scheme, domain, path) for a relative path."""
    return urljoin(SCHEME + get_domain(), path)


def request_access_token(install):
    """Request access token from API.

    Pulled out as a function to allow for mocking.

    Args:
        install: an Install object for which we are requesting a token.

    Returns the output from requests.post(...).json()

    """
    url = "https://api.hipchat.com/v2/oauth/token"
    resp = requests.post(url, auth=install.http_auth(), data=install.token_request_data())
    return resp.json()


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
        return "<Scope id=%s name='%s'>" % (self.id, self.name.encode('utf-8'))

    def save(self, *args, **kwargs):
        super(Scope, self).save(*args, **kwargs)
        return self


class Addon(models.Model):

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
        return "<Addon id=%s key='%s'>" % (self.id, self.key.encode('utf-8'))

    def get_absolute_url(self):
        return reverse('hipchat:descriptor', kwargs={'app_id': self.id})

    def descriptor_url(self):
        """Format the fully-qualified URL for the descriptor."""
        if self.id is None:
            return None
        return get_full_url(self.get_absolute_url())

    def install_url(self):
        """Format the fully-qualified URL for the descriptor."""
        if self.id is None:
            return None
        return get_full_url(reverse('hipchat:install', kwargs={'app_id': self.id}))

    def scopes_as_list(self):
        """Return related scopes as a list."""
        return sorted([s.name for s in self.scopes.all()])

    def scopes_as_string(self):
        """Return related scopes as a space-separated string."""
        return ' '.join(self.scopes_as_list())

    def descriptor(self):
        """Return the object formatted as the HipChat add-on descriptor."""
        if self.id is None:
            return None
        descriptor = {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "vendor": {
                "name": self.vendor_name,
                "url": self.vendor_url
            },
            "links": {
                "self": self.descriptor_url(),
            },
            "capabilities": {
                "hipchatApiConsumer": {
                    "scopes": self.scopes_as_list()
                },
                "installable": {
                    "callbackUrl": self.install_url(),
                    "allowGlobal": self.allow_global,
                    "allowRoom": self.allow_room
                },
            },
        }
        if self.glances.exists():
            descriptor["glance"] = [g.descriptor() for g in self.glances.all()]
        return descriptor

    def save(self, *args, **kwargs):
        super(Addon, self).save(*args, **kwargs)
        return self


class Install(models.Model):

    """Store data returned from the HipChat API re. an app install.

    Specific information required for access rights - see
    https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

    """

    app = models.ForeignKey(
        Addon,
        help_text="App to which this access info belongs."
    )
    # the following attrs are set by the install postback from HipChat
    oauth_id = models.CharField(
        max_length=20,
        help_text="Value returned from the app install postback.",
        unique=True,
        db_index=True
    )
    oauth_secret = models.CharField(
        max_length=20,
        help_text="Value returned from the app install postback."
    )
    group_id = models.IntegerField(
        blank=True,
        help_text="Value returned from the app install postback."
    )
    room_id = models.IntegerField(
        blank=True, null=True,
        help_text="Value returned from the app install postback."
    )
    installed_at = models.DateTimeField(
        help_text="Timestamp set when the app is installed."
    )

    def __unicode__(self):
        return u"%s" % (self.oauth_id.split('-')[0])

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<Install id=%s app=%s>" % (self.id, self.app.id)

    def save(self, *args, **kwargs):
        self.installed_at = self.installed_at or tz_now()
        super(Install, self).save(*args, **kwargs)
        return self

    def http_auth(self):
        """Return HTTPBasicAuth object using oauth_id, secret."""
        return HTTPBasicAuth(self.oauth_id, self.oauth_secret)

    def parse_json(self, json_data):
        """Set object properties from the HipChat API callback JSON.

        The callback POSTs JSON that looks like this:

        {
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "oauthId": "abc",
            "oauthSecret": "xyz",
            "groupId": 123,
            "roomId": "1234"
        }

        NB this method doesn't save the object.

        """
        self.oauth_id = json_data['oauthId']
        self.oauth_secret = json_data['oauthSecret']
        self.group_id = json_data['groupId']
        if 'roomId' in json_data:
            self.room_id = int(json_data['roomId'])
        return self

    def token_request_data(self):
        """Return JSON data for POSTing to token request API."""
        return {
            'grant_type': 'client_credentials',
            'scope': self.app.scopes_as_string()
        }

    def get_access_token(self):
        """Fetch a new access_token from HipChat for this install.

        This method is used to fill in the second half of the app install
        properties - including the access_token, which is the token used
        when calling the HipChat API.

        """
        token_data = request_access_token(self)
        token = AccessToken(app=self.app, install=self)
        token.parse_json(token_data)
        return token.save()


class AccessToken(models.Model):

    """Store specific access tokens, and their scopes."""

    app = models.ForeignKey(
        Addon,
        help_text="None if a personal token.",
        blank=True, null=True
    )
    install = models.ForeignKey(
        Install,
        help_text="None if a personal token.",
        blank=True, null=True
    )
    group_id = models.IntegerField(
        blank=True,
        help_text="The HipChat group ID this token belongs to"
    )
    group_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="The HipChat group name this token belongs to."
    )
    access_token = models.CharField(
        max_length=40,
        help_text="The generated access token to use to authenticate future requests.",
        blank=True,
        unique=True,
        db_index=True
    )
    expires_at = models.DateTimeField(
        blank=True, null=True,
        help_text="The datetime at which this token will expire."
    )
    scope = models.CharField(
        max_length=500,
        blank=True,
        help_text="A space-delimited list of scopes that this token is allowed to use."
    )
    created_at = models.DateTimeField(
        help_text="Set when this object is first saved."
    )
    # included for API completeness only
    token_type = 'bearer'

    def __unicode__(self):
        return u"%s" % self.access_token[:6]

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<AccessToken id=%s token='%s'>" % (self.id, self.access_token[:6])

    def save(self, *args, **kwargs):
        self.created_at = self.created_at or tz_now()
        super(AccessToken, self).save(*args, **kwargs)
        return self

    @property
    def has_expired(self):
        """Return True if the token has gone past its expiry date."""
        return self.expires_at is None or self.expires_at < tz_now()

    def set_expiry(self, seconds):
        """Set the expires_at value a number of seconds into the future.

        NB This method does *not* save the object.

        """
        self.expires_at = tz_now() + datetime.timedelta(seconds=seconds)

    def parse_json(self, json_data):
        """Set object properties from the token API response data.

        https://www.hipchat.com/docs/apiv2/method/generate_token

        This is a sample:

        {
          access_token: '5236346233724572457245gdgreyt345yreg',
          expires_in: 431999999,
          group_id: 123,
          group_name: 'Example Company',
          scope: 'send_notification',
          token_type: 'bearer'
        }

        NB This method does not save the object.

        """
        self.access_token = json_data['access_token']
        self.group_id = json_data['group_id']
        self.group_name = json_data['group_name']
        self.scope = json_data['scope']
        self.set_expiry(json_data['expires_in'])
        return self


class Glance(models.Model):

    """HipChat glance descriptor."""

    app = models.ForeignKey(
        Addon,
        help_text="The app this glance belongs to.",
        related_name='glances'
    )
    key = models.CharField(
        max_length=40,
        help_text="Unique key (in the context of the integration) to identify this glance."
    )
    name = models.CharField(
        max_length=100,
        help_text="The display name of the glance.",
        blank=True
    )
    data_url = models.URLField(
        blank=True,
        help_text=("REST endpoint exposed by the add-on for Glance data.")
    )
    target = models.CharField(
        max_length="40",
        blank=True,
        help_text="The key of a sidebar web panel, dialog or external page."
    )
    icon_url = models.URLField(
        blank=True,
        help_text="URL to icon displayed on the left of the glance."
    )
    icon_url2 = models.URLField(
        blank=True,
        help_text="URL to hi-res icon displayed on the left of the glance."
    )

    def __unicode__(self):
        return self.key

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "<Glance id=%s key='%s'>" % (self.id, self.key.encode('utf-8'))

    def get_absolute_url(self):
        return reverse('hipchat:glance', kwargs={'glance_id': self.id})

    def query_url(self):
        """Return full URL - including scheme and domain."""
        if self.data_url == '':
            return get_full_url(self.get_absolute_url())
        else:
            return self.data_url

    def save(self, *args, **kwargs):
        super(Glance, self).save(*args, **kwargs)
        return self

    def descriptor(self):
        """Return JSON descriptor for the Glance."""
        return {
            "name": {
                "value": self.name
            },
            "queryUrl": self.query_url(),
            "key": self.key,
            "target": self.target,
            "icon": {
                "url": self.icon_url,
                "url@2x": self.icon_url2
            }
        }


class GlanceUpdate(models.Model):

    """Container for Glance data response.

    This is stored as an object so that we can contain a complete,
    centralised, record of all glance updates. If it gets out of hand,
    truncate the table.

    https://ecosystem.atlassian.net/wiki/display/HIPDEV/HipChat+Glances

    """

    LOZENGE_EMPTY = 'empty'
    LOZENGE_DEFAULT = 'default'
    LOZENGE_SUCCESS = 'success'
    LOZENGE_CURRENT = 'current'
    LOZENGE_COMPLETE = 'complete'
    LOZENGE_ERROR = 'error'
    LOZENGE_NEW = 'new'
    LOZENGE_MOVED = 'moved'

    LOZENGE_CHOICES = (
        (LOZENGE_EMPTY, 'no lozenge'),
        (LOZENGE_DEFAULT, 'default'),
        (LOZENGE_SUCCESS, ' success'),
        (LOZENGE_CURRENT, ' current'),
        (LOZENGE_COMPLETE, 'complete'),
        (LOZENGE_ERROR, 'error'),
        (LOZENGE_NEW, 'new'),
        (LOZENGE_MOVED, 'moved')
    )

    glance = models.ForeignKey(
        Glance,
        help_text="The Glance that this data updated."
    )
    # fixed const - may change in future
    label_type = 'html'
    label_value = models.CharField(
        max_length=1000,
        help_text="HTML displayed in the glance body."
    )
    lozenge_type = models.CharField(
        max_length=10,
        choices=LOZENGE_CHOICES,
        default=LOZENGE_EMPTY
    )
    lozenge_value = models.CharField(
        max_length=20,
        blank=True,
        help_text="Text displayed inside the lozenge."
    )
    icon_url = models.URLField(
        blank=True,
        help_text="URL to icon displayed on the right of the glance."
    )
    icon_url2 = models.URLField(
        blank=True,
        help_text="URL to hi-res icon displayed on the right of the glance."
    )
    metadata = models.TextField(
        blank=True,
        help_text="Arbitrary JSON sent as the metadata value."
    )

    @property
    def has_lozenge(self):
        return self.lozenge_type != GlanceUpdate.LOZENGE_EMPTY

    @property
    def has_icon(self):
        return self.icon_url not in (None, '')

    @property
    def has_metadata(self):
        return self.metadata not in (None, '')

    def save(self, *args, **kwargs):
        super(GlanceUpdate, self).save(*args, **kwargs)
        return self

    def label(self):
        """Return the glance label as JSON."""
        return {'type': self.label_type, 'value': self.label_value}

    def status(self):
        """Return the glance status as JSON."""
        if self.has_lozenge:
            return {
                'type': 'lozenge',
                'value': {
                    'type': self.lozenge_type,
                    'label': self.lozenge_value
                }
            }
        elif self.has_icon:
            return {
                'type': 'icon',
                'value': {
                    'url': self.icon_url,
                    'url@2x': self.icon_url2
                }
            }
        return {}

    def content(self):
        """Return the JSON data to be posted to the API."""
        content = {
            'status': self.status(),
            'label': self.label(),
        }
        if self.has_metadata:
            content['metadata'] = self.metadata
        return content
