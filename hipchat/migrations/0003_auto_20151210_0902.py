# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0002_auto_20151210_0409'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.IntegerField(help_text=b'Value returned from the token request.', blank=True)),
                ('group_name', models.CharField(help_text=b'Value returned from the token request.', max_length=100, blank=True)),
                ('room_id', models.IntegerField(help_text=b'Value returned from the token request.', null=True, blank=True)),
                ('token', models.CharField(help_text=b'Value returned from the token request.', unique=True, max_length=40, db_index=True, blank=True)),
                ('expires_at', models.DateTimeField(help_text=b'The datetime at which this token will expire.', null=True, blank=True)),
                ('scope', models.CharField(help_text=b'List of scopes, returned from the token request.', max_length=500, blank=True)),
                ('created_at', models.DateTimeField()),
                ('app', models.ForeignKey(blank=True, to='hipchat.HipChatApp', help_text=b'None if a personal token.', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='appinstall',
            name='access_token',
        ),
        migrations.RemoveField(
            model_name='appinstall',
            name='expires_at',
        ),
        migrations.RemoveField(
            model_name='appinstall',
            name='scope',
        ),
        migrations.AlterField(
            model_name='appinstall',
            name='group_id',
            field=models.IntegerField(help_text=b'Value returned from the app install postback.', blank=True),
        ),
        migrations.AlterField(
            model_name='appinstall',
            name='oauth_id',
            field=models.CharField(help_text=b'Value returned from the app install postback.', unique=True, max_length=20, db_index=True),
        ),
        migrations.AlterField(
            model_name='appinstall',
            name='oauth_secret',
            field=models.CharField(help_text=b'Value returned from the app install postback.', max_length=20),
        ),
        migrations.AlterField(
            model_name='appinstall',
            name='room_id',
            field=models.IntegerField(help_text=b'Value returned from the app install postback.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='install',
            field=models.ForeignKey(blank=True, to='hipchat.AppInstall', help_text=b'None if a personal token.', null=True),
        ),
    ]
