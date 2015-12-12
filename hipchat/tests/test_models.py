# -*- coding: utf-8 -*-
import mock
import random

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase

from hipchat.models import (
    Scope,
    HipChatApp,
    AppInstall,
    AccessToken,
    Glance,
    get_full_url,
    get_domain,
    request_access_token,
    SCHEME
)


class MockResponse(object):

    """Mock used to fake the requests reponse object."""

    def json(self):
        return {'hello': 'world'}


def mock_requests_post(*args, **kwargs):
    """Mock for requests.post function.

    This allows us to have deterministic output from
    json method

    """
    return MockResponse()


class FunctionTests(TestCase):

    """Free function tests."""

    def test_get_domain(self):
        site = Site.objects.get()
        self.assertEqual(get_domain(), site.domain)

    @mock.patch('hipchat.models.get_domain', lambda: 'foo.com')
    def test_get_full_url(self):
        self.assertEqual(get_full_url("foo"), "https://foo.com/foo")
        self.assertEqual(get_full_url("/foo"), "https://foo.com/foo")

    @mock.patch('requests.post', mock_requests_post)
    @mock.patch('hipchat.models.AppInstall.http_auth', lambda x: {})
    @mock.patch('hipchat.models.AppInstall.token_request_data', lambda x: {})
    def test_request_access_token(self):
        # This is a bit of fudge - we're really only validating that
        # the function calls the post function and returns the json value.
        self.assertEqual(
            request_access_token(AppInstall()),
            {'hello': 'world'}
        )


class HipChatAppModelTests(TransactionTestCase):

    """Test suite for the HipChatApp model attrs and methods."""

    fixtures = ['scopes.json']

    def test_strings(self):
        key = u"∂ƒ©˙∆˚"
        app = HipChatApp(key=key)
        self.assertEqual(unicode(app), key)
        self.assertEqual(str(app), key.encode('utf-8'))
        self.assertEqual(repr(app), "<HipChatApp id=None key='%s'>" % (key.encode('utf-8')))

    def test_save(self):
        app = HipChatApp()
        self.assertEqual(app.save(), app)
        self.assertIsNotNone(app.id, None)

    @mock.patch('hipchat.models.get_domain', lambda: 'foo.com')
    def test_descriptor_url(self):
        app = HipChatApp()
        self.assertIsNone(app.descriptor_url())
        app.save()
        url = get_full_url(app.get_absolute_url())
        self.assertEqual(app.descriptor_url(), url)

    @mock.patch('hipchat.models.get_domain', lambda: 'foo.com')
    def test_install_url(self):
        app = HipChatApp()
        self.assertIsNone(app.install_url())
        app.save()
        url = reverse('hipchat:install', kwargs={'app_id': app.id})
        self.assertEqual(app.install_url(), get_full_url(url))

    def test_scopes_as_list(self):
        app = HipChatApp().save()
        scopes = random.sample(list(Scope.objects.all()), 3)
        for scope in scopes:
            app.scopes.add(scope)
        scopes_list = [s.name for s in scopes]
        self.assertEqual(app.scopes_as_list(), sorted(scopes_list))

    def test_scopes_as_string(self):
        app = HipChatApp()
        with mock.patch('hipchat.models.HipChatApp.scopes_as_list', lambda x: []):
            self.assertEqual(app.scopes_as_string(), "")
        with mock.patch('hipchat.models.HipChatApp.scopes_as_list', lambda x: ['x']):
            self.assertEqual(app.scopes_as_string(), "x")
        with mock.patch('hipchat.models.HipChatApp.scopes_as_list', lambda x: ['x', 'y']):
            self.assertEqual(app.scopes_as_string(), "x y")

    @mock.patch('hipchat.models.get_domain', lambda: 'foo.com')
    def test_descriptor(self):
        app = HipChatApp()
        app.key = "key"
        app.name = "name"
        app.description = "description"
        app.vendor_name = "ACME"
        app.vendor_url = "example.com"
        app.allow_global = True
        app.allow_room = True
        # before saving we have no URLs to call back to
        # so the descriptor is null
        self.assertEqual(app.descriptor(), None)

        app.save()

        expected = {
            "key": "key",
            "name": "name",
            "description": "description",
            "vendor": {
                "name": "ACME",
                "url": "example.com"
            },
            "links": {
                "self": app.descriptor_url(),
            },
            "capabilities": {
                "hipchatApiConsumer": {
                    "scopes": []
                },
                "installable": {
                    "callbackUrl": app.install_url(),
                    "allowGlobal": True,
                    "allowRoom": True
                },
            },
            # "glance": [g.descriptor() for g in self.glances.all()]
        }
        self.assertEqual(app.descriptor(), expected)

        app.scopes.add(Scope.objects.first())
        scopes = app.descriptor()['capabilities']['hipchatApiConsumer']['scopes']
        self.assertEqual(scopes, app.scopes_as_list())

        glance = Glance(app=app, key='key').save()
        app.glances.add(glance)
        self.assertEqual(app.descriptor()['glance'], [glance.descriptor()])


class ScopeModelTests(TransactionTestCase):

    """Test suite for Scope model attrs and methods."""

    fixtures = ['scopes.json']

    def test_strings(self):
        name = u"∂ƒ©˙∆˚"
        obj = Scope(name=name)
        self.assertEqual(unicode(obj), name)
        self.assertEqual(str(obj), name.encode('utf-8'))
        self.assertEqual(repr(obj), "<Scope id=None name='%s'>" % (name.encode('utf-8')))

    def test_save(self):
        scope = Scope()
        self.assertEqual(scope.save(), scope)
        self.assertIsNotNone(scope.id)


class AppInstallModelTests(TransactionTestCase):

    """Test suite for AppInstall model attrs and methods."""

    fixtures = ['scopes.json']

    def setUp(self):
        self.app = HipChatApp(key=u"∂ƒ©˙∆˚").save()
        self.install = AppInstall(app=self.app, group_id=0)
        self.assertIsNone(self.install.installed_at)
        self.install.save()
        self.assertIsNotNone(self.install.installed_at)

    def test_strings(self):
        obj = self.install
        # confirm they don't blow up.
        self.assertIsNotNone(unicode(obj))
        self.assertIsNotNone(str(obj))
        self.assertIsNotNone(repr(obj))

    def test_save(self):
        obj = self.install.save()
        # we're just confirming that the save method
        # returns self
        self.assertIsNotNone(obj)

    def test_http_auth(self):
        obj = AppInstall(oauth_id="foo", oauth_secret="bar")
        auth = obj.http_auth()
        self.assertEqual(auth.username, obj.oauth_id)
        self.assertEqual(auth.password, obj.oauth_secret)

    def test_parse_json(self):
        data = {
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "oauthId": "abc",
            "oauthSecret": "xyz",
            "groupId": 123,
            # "roomId": "1234"
        }
        obj = self.install.parse_json(data)
        self.assertEqual(obj.oauth_id, 'abc')
        self.assertEqual(obj.oauth_secret, 'xyz')
        self.assertEqual(obj.group_id, 123)
        self.assertEqual(obj.room_id, None)
        data['roomId'] = '123'
        obj = self.install.parse_json(data)
        self.assertEqual(obj.room_id, '123')

    def test_token_request_data(self):
        obj = self.install
        with mock.patch('hipchat.models.HipChatApp.scopes_as_string', lambda x: 'foo'):
            self.assertEqual(
                obj.token_request_data(),
                {'scope': 'foo', 'grant_type': 'client_credentials'}
            )

    def test_get_access_token(self):
        token_data = {
            'access_token': '52363462337245724',
            'expires_in': 3599,
            'group_id': 123,
            'group_name': 'Example Company',
            'scope': 'send_notification',
            'token_type': 'bearer'
        }
        self.assertFalse(AccessToken.objects.exists())
        with mock.patch('hipchat.models.request_access_token', lambda x: token_data):
            token = self.install.get_access_token()
            self.assertEqual(token, AccessToken.objects.get())
            self.assertEqual(token.app, self.app)
            self.assertEqual(token.install, self.install)
            self.assertEqual(token.group_id, 123)
            self.assertEqual(token.group_name, 'Example Company')
            self.assertEqual(token.scope, 'send_notification')
            self.assertIsNotNone(token.created_at)
