# -*- coding: utf-8 -*-
"""hipchat models.

https://ecosystem.atlassian.net/wiki/display/HIPDEV/Server-side+installation+flow

"""
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.timezone import now as tz_now


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

    @property
    def descriptor_url(self):
        """Format the fully-qualified URL for the descriptor."""
        return reverse('hipchat:descriptor', kwargs={'id': self.id})

    @property
    def install_url(self):
        """Format the fully-qualified URL for the descriptor."""
        return reverse('hipchat:install', kwargs={'id': self.id})

    @property
    def scopes_list(self):
        """Return related scopes as a comma-separated string."""
        return [s.name for s in self.scopes_set.all()]

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
                    "callbackUrl": self.install_url
                },
            }
        }
        descriptor['capabilities']['hipchatApiConsumer']['scopes']

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
        data = AppInstall(app=app)
        data.oauth_id = data['oauthId']
        data.oauth_secret = data['oauthSecret']
        data.group_id = data['groupId']
        data.room_id = data['roomId']
        return data.save()


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
    oauth_id = models.CharField(
        max_length=20,
        help_text="OAuth ID returned from the app install postback."
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
    access_token = models.CharField(
        max_length=40,
        help_text="API access token",
        blank=True
    )
    expires_in = models.DateTimeField(
        blank=True, null=True,
        help_text="The datetime at which this access_token will expire."
    )
    scope = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma separated list of scopes."
    )

    objects = AppInstallQuerySet.as_manager()

    def save(self, *args, **kwargs):
        super(AppInstall, self).save(*args, **kwargs)
        return self
