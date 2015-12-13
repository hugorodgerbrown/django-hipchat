# -*- coding: utf-8 -*-
import json
import mock

# from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TransactionTestCase, RequestFactory

from hipchat import models
from hipchat import signals
from hipchat import views


class ViewTests(TransactionTestCase):

    """Test suite for promoter score views."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_descriptor_200(self):
        app = models.Addon().save()
        request = self.factory.get('/')
        resp = views.descriptor(request, app_id=app.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps(app.descriptor()))

    def test_descriptor_404(self):
        request = self.factory.get('/')
        self.assertRaises(Http404, views.descriptor, request, app_id=0)

    def test_install_201(self):
        app = models.Addon().save()
        data = {
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "oauthId": "abc",
            "oauthSecret": "xyz",
            "groupId": 123,
            "roomId": "1234"
        }
        self.assertFalse(models.Install.objects.exists())
        request = self.factory.post(
            '/',
            json.dumps(data),
            content_type='application/json'
        )

        token_data = {
            'access_token': '52363462337245724',
            'expires_in': 3599,
            'group_id': 123,
            'group_name': 'Example Company',
            'scope': 'send_notification',
            'token_type': 'bearer'
        }
        with mock.patch('hipchat.models.request_access_token', lambda x: token_data):
            resp = views.install(request, app_id=app.id)
        self.assertEqual(resp.status_code, 201)
        install = models.Install.objects.get()
        self.assertEqual(install.oauth_id, data['oauthId'])
        self.assertEqual(install.oauth_secret, data['oauthSecret'])
        self.assertEqual(install.group_id, data['groupId'])
        self.assertEqual(install.room_id, int(data['roomId']))

    def test_install_422(self):
        app = models.Addon().save()
        models.Install(app=app, oauth_id="abc", group_id=0).save()
        data = {
            "capabilitiesUrl": "https://api.hipchat.com/v2/capabilities",
            "oauthId": "abc",
            "oauthSecret": "xyz",
            "groupId": 123,
            "roomId": "1234"
        }
        request = self.factory.post(
            '/',
            json.dumps(data),
            content_type='application/json'
        )
        resp = views.install(request, app_id=app.id)
        self.assertEqual(resp.status_code, 422)

    def test_delete_204(self):
        app = models.Addon().save()
        install = models.Install(app=app, oauth_id="abc", group_id=0).save()
        request = self.factory.delete('/')
        resp = views.delete(request, app_id=app.id, oauth_id=install.oauth_id)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(models.Install.objects.exists())

    def test_delete_404(self):
        request = self.factory.delete('/')
        self.assertRaises(Http404, views.delete, request, app_id=0, oauth_id=0)

    def test_glance_200_no_handlers(self):
        self.app = models.Addon(key=u"∂ƒ©˙∆˚").save()
        self.glance = models.Glance(app=self.app).save()
        self.assertEqual(models.GlanceUpdate.objects.count(), 0)
        request = self.factory.get('/')
        resp = views.glance(request, glance_id=self.glance.id)
        self.assertEqual(resp.status_code, 200)
        update = models.GlanceUpdate.objects.get()
        self.assertEqual(resp.content, json.dumps(update.content()))

    def test_glance_200(self):
        self.app = models.Addon(key=u"∂ƒ©˙∆˚").save()
        self.glance = models.Glance(app=self.app).save()
        request = self.factory.get('/')

        def on_glance_data_request(sender, **kwargs):
            return models.GlanceUpdate(
                glance=kwargs['glance'],
            )

        signals.glance_data_requested.connect(on_glance_data_request)

        resp = views.glance(request, glance_id=self.glance.id)
        self.assertEqual(resp.status_code, 200)
        update = models.GlanceUpdate.objects.get()
        self.assertEqual(resp.content, json.dumps(update.content()))

    def test_glance_404(self):
        request = self.factory.get('/')
        self.assertRaises(Http404, views.glance, request, glance_id=0)
