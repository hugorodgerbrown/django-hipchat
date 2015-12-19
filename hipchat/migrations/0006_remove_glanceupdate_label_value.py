# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0005_auto_20151216_0347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='glanceupdate',
            name='label_value',
        ),
    ]
