# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0003_auto_20151210_0902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesstoken',
            name='room_id',
        ),
        migrations.RemoveField(
            model_name='accesstoken',
            name='token',
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='access_token',
            field=models.CharField(help_text=b'The generated access token to use to authenticate future requests.', unique=True, max_length=40, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='group_id',
            field=models.IntegerField(help_text=b'The HipChat group ID this token belongs to', blank=True),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='group_name',
            field=models.CharField(help_text=b'The HipChat group name this token belongs to.', max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='scope',
            field=models.CharField(help_text=b'A space-delimited list of scopes that this token is allowed to use.', max_length=500, blank=True),
        ),
    ]
