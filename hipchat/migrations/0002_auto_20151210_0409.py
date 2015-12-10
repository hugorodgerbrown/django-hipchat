# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appinstall',
            old_name='expires_in',
            new_name='expires_at',
        ),
        migrations.AddField(
            model_name='appinstall',
            name='installed_at',
            field=models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), help_text=b'Timestamp set when the app is installed.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appinstall',
            name='oauth_id',
            field=models.CharField(help_text=b'OAuth ID returned from the app install postback.', unique=True, max_length=20),
        ),
    ]
