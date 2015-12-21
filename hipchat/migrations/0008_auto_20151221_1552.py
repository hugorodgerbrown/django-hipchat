# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0007_glanceupdate_label_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='install',
            name='access_token',
        ),
        migrations.RemoveField(
            model_name='install',
            name='expires_at',
        ),
        migrations.RemoveField(
            model_name='install',
            name='group_name',
        ),
        migrations.RemoveField(
            model_name='install',
            name='last_updated_at',
        ),
        migrations.RemoveField(
            model_name='install',
            name='scope',
        ),
    ]
