# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0006_remove_glanceupdate_label_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='glanceupdate',
            name='label_value',
            field=models.CharField(default='foo', help_text=b'HTML displayed in the glance body.', max_length=1000),
            preserve_default=False,
        ),
    ]
