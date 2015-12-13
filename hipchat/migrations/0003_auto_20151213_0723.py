# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0002_auto_20151213_0657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glance',
            name='icon_url',
            field=models.URLField(help_text=b'URL to icon displayed on the left of the glance.', blank=True),
        ),
        migrations.AlterField(
            model_name='glance',
            name='icon_url2',
            field=models.URLField(help_text=b'URL to hi-res icon displayed on the left of the glance.', blank=True),
        ),
    ]
