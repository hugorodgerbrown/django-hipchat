# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0003_auto_20151213_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='install',
            name='access_token',
            field=models.CharField(help_text=b'API access token used to authenticate future requests.', unique=True, max_length=40, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='install',
            name='expires_at',
            field=models.DateTimeField(help_text=b'The datetime at which this token will expire.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='install',
            name='group_name',
            field=models.CharField(help_text=b'The name of the group (company) HipChat account.', max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='install',
            name='last_updated_at',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), help_text=b'Set when the object is updated.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='install',
            name='scope',
            field=models.CharField(help_text=b'A space-delimited list of scopes that this token is allowed to use.', max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='install',
            name='group_id',
            field=models.IntegerField(help_text=b'The Id of the group (company) HipChat account.', blank=True),
        ),
        migrations.AlterField(
            model_name='install',
            name='installed_at',
            field=models.DateTimeField(help_text=b'Set when the object is created (post-installation).'),
        ),
        migrations.AlterField(
            model_name='install',
            name='room_id',
            field=models.IntegerField(help_text=b'The id of the room into which the app was installed (blank if global).', null=True, blank=True),
        ),
    ]
