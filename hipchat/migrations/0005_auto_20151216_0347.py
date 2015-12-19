# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0004_auto_20151215_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesstoken',
            name='app',
        ),
        migrations.RemoveField(
            model_name='accesstoken',
            name='install',
        ),
        migrations.DeleteModel(
            name='AccessToken',
        ),
    ]
