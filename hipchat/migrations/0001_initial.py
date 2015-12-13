# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.IntegerField(help_text=b'The HipChat group ID this token belongs to', blank=True)),
                ('group_name', models.CharField(help_text=b'The HipChat group name this token belongs to.', max_length=100, blank=True)),
                ('access_token', models.CharField(help_text=b'The generated access token to use to authenticate future requests.', unique=True, max_length=40, db_index=True, blank=True)),
                ('expires_at', models.DateTimeField(help_text=b'The datetime at which this token will expire.', null=True, blank=True)),
                ('scope', models.CharField(help_text=b'A space-delimited list of scopes that this token is allowed to use.', max_length=500, blank=True)),
                ('created_at', models.DateTimeField(help_text=b'Set when this object is first saved.')),
            ],
        ),
        migrations.CreateModel(
            name='Addon',
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
            name='Glance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b'Unique key (in the context of the integration) to identify this glance.', max_length=40)),
                ('name', models.CharField(help_text=b'The display name of the glance.', max_length=100, blank=True)),
                ('data_url', models.URLField(help_text=b'REST endpoint exposed by the add-on for Glance data.', blank=True)),
                ('target', models.CharField(help_text=b'The key of a sidebar web panel, dialog or external page.', max_length=b'40', blank=True)),
                ('app', models.ForeignKey(related_name='glances', to='hipchat.Addon', help_text=b'The app this glance belongs to.')),
            ],
        ),
        migrations.CreateModel(
            name='GlanceUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label_value', models.CharField(help_text=b'HTML displayed in the glance body.', max_length=1000)),
                ('lozenge_type', models.CharField(default=b'empty', max_length=10, choices=[(b'empty', b'no lozenge'), (b'default', b'default'), (b'success', b' success'), (b'current', b' current'), (b'complete', b'complete'), (b'error', b'error'), (b'new', b'new'), (b'moved', b'moved')])),
                ('lozenge_value', models.CharField(help_text=b'Text displayed inside the lozenge.', max_length=20, blank=True)),
                ('icon_url', models.URLField(help_text=b'URL to icon displayed on the right of the glance.', blank=True)),
                ('icon_url2', models.URLField(help_text=b'URL to hi-res icon displayed on the right of the glance.', blank=True)),
                ('metadata', models.TextField(help_text=b'Arbitrary JSON sent as the metadata value.', blank=True)),
                ('glance', models.ForeignKey(help_text=b'The Glance that this data updated.', to='hipchat.Glance')),
            ],
        ),
        migrations.CreateModel(
            name='Install',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oauth_id', models.CharField(help_text=b'Value returned from the app install postback.', unique=True, max_length=20, db_index=True)),
                ('oauth_secret', models.CharField(help_text=b'Value returned from the app install postback.', max_length=20)),
                ('group_id', models.IntegerField(help_text=b'Value returned from the app install postback.', blank=True)),
                ('room_id', models.IntegerField(help_text=b'Value returned from the app install postback.', null=True, blank=True)),
                ('installed_at', models.DateTimeField(help_text=b'Timestamp set when the app is installed.')),
                ('app', models.ForeignKey(help_text=b'App to which this access info belongs.', to='hipchat.Addon')),
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
            model_name='addon',
            name='scopes',
            field=models.ManyToManyField(help_text=b'List of security scopes you need, which will dictate what REST APIs your add-on can call.', to='hipchat.Scope'),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='app',
            field=models.ForeignKey(blank=True, to='hipchat.Addon', help_text=b'None if a personal token.', null=True),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='install',
            field=models.ForeignKey(blank=True, to='hipchat.Install', help_text=b'None if a personal token.', null=True),
        ),
    ]
