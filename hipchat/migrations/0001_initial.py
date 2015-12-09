# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppInstall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oauth_id', models.CharField(help_text=b'OAuth ID returned from the app install postback.', max_length=20)),
                ('oauth_secret', models.CharField(help_text=b'OAuth secret returned from the app install postback.', max_length=20)),
                ('group_id', models.IntegerField(help_text=b'Name of the group, returned from the token URL.', blank=True)),
                ('room_id', models.IntegerField(help_text=b'Id of the room into which the app was installed.', null=True, blank=True)),
                ('access_token', models.CharField(help_text=b'API access token', max_length=40, blank=True)),
                ('expires_in', models.DateTimeField(help_text=b'The datetime at which this access_token will expire.', null=True, blank=True)),
                ('scope', models.CharField(help_text=b'Comma separated list of scopes.', max_length=500, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HipChatApp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b'Has to be unique', unique=True, max_length=100)),
                ('name', models.CharField(help_text=b'Name of your add-on, will be shown to users when they install your integration.', max_length=100)),
                ('description', models.CharField(help_text=b'Description of your add-on, will be shown to users when they install your integration.', max_length=200, blank=True)),
                ('vendor_name', models.CharField(help_text=b'Name of your company (will be shown to users when they install your integration).', max_length=100)),
                ('vendor_url', models.URLField(help_text=b'Company website (will be shown to users when they install you integration).')),
                ('allow_global', models.BooleanField(default=False, help_text=b'Set to True if your addon can be installed globally (which makes it accessible in all rooms).')),
                ('allow_room', models.BooleanField(default=False, help_text=b'Set to true if your addon can be installed in a room.')),
            ],
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the scope as required by HipChat.', max_length=25)),
                ('description', models.CharField(help_text=b'The capabilities allowed within this scope.', max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='hipchatapp',
            name='scopes',
            field=models.ManyToManyField(help_text=b'List of security scopes you need, which will dictate what REST APIs your add-on can call.', to='hipchat.Scope'),
        ),
        migrations.AddField(
            model_name='appinstall',
            name='app',
            field=models.ForeignKey(help_text=b'App to which this access info belongs.', to='hipchat.HipChatApp'),
        ),
    ]
