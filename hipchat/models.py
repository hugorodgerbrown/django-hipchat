# -*- coding: utf-8 -*-
"""hipchat models.

https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

"""
import datetime
import json
import logging
from urlparse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.timezone import now as tz_now

USE_SSL = getattr(settings, 'USE_SSL', True)

logger = logging.getLogger(__name__)


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
        """Return related scopes as a list."""
        return [s.name for s in self.scopes.all()]

    @property
    def scopes_string(self):
        """Return related scopes as a space-separated string."""
        return ' '.join(self.scopes_list)

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
        descriptor['glance'] = [g.descriptor for g in self.glances.all()]
        return descriptor

    def save(self, *args, **kwargs):
        super(HipChatApp, self).save(*args, **kwargs)
        return self


class AppInstall(models.Model):

    """Store data returned from the HipChat API re. an app install.

    Specific information required for access rights - see
    https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

    """

    app = models.ForeignKey(
        HipChatApp,
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
        return u"%s (%s)" % (self.app, self.oauth_id)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<AppInstall id=%s app=%s>" % (self.id, self.app.id)

    def save(self, *args, **kwargs):
        self.installed_at = self.installed_at or tz_now()
        super(AppInstall, self).save(*args, **kwargs)
        return self

    @property
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
            self.room_id = json_data['roomId']
        return self

    def get_access_token(self):
        """Fetch a new access_token from HipChat for this install.

        This method is used to fill in the second half of the app install
        properties - including the access_token, which is the token used
        when calling the HipChat API.

        """
        url = "https://api.hipchat.com/v2/oauth/token"
        client_data = {'grant_type': 'client_credentials', 'scope': self.app.scopes_string}  # noqa
        logger.debug("Requesting token: %s", json.dumps(client_data))
        resp = requests.post(url, auth=self.http_auth, data=client_data)
        resp_data = resp.json()
        logger.debug("Token response: %s", json.dumps(resp_data))
        token = AccessToken(app=self.app, install=self)
        token.parse_json(resp_data)
        return token.save()


class AccessToken(models.Model):

    """Store specific access tokens, and their scopes."""
    app = models.ForeignKey(
        HipChatApp,
        help_text="None if a personal token.",
        blank=True, null=True
    )
    install = models.ForeignKey(
        AppInstall,
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

    def __unicode__(self):
        return u"%s" % self.access_token

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<AccessToken id=%s token='%s'>" % (self.id, self.access_token)

    def save(self, *args, **kwargs):
        self.created_at = self.created_at or tz_now()
        super(AccessToken, self).save(*args, **kwargs)
        return self

    @property
    def has_expired(self):
        """Return True if the token has gone past its expiry date."""
        return self.expires_at < tz_now()

    # included for API completeness only
    @property
    def token_type(self):
        return 'bearer'

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
        HipChatApp,
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

    def __unicode__(self):
        return u"%s" % self.key

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return u"<Glance id=%s key='%s'>" % (self.id, self.key)

    def get_absolute_url(self):
        return reverse('hipchat:glance', kwargs={'glance_id': self.id})

    def get_full_url(self):
        """Return full URL - including scheme and domain."""    
        return get_full_url(self.get_absolute_url())

    def save(self, *args, **kwargs):
        super(Glance, self).save(*args, **kwargs)
        return self

    @property
    def descriptor(self):
        """Return JSON descriptor for the Glance."""
        descriptor = {
            "name": {
                "value": self.name
            },
            "queryUrl": self.get_full_url(),
            "key": self.key,
            "target": "foo"
        }
        return descriptor
