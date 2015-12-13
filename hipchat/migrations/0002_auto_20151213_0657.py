# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='glance',
            name='icon_url',
            field=models.URLField(help_text=b'URL to icon displayed on the right of the glance.', blank=True),
        ),
        migrations.AddField(
            model_name='glance',
            name='icon_url2',
            field=models.URLField(help_text=b'URL to hi-res icon displayed on the right of the glance.', blank=True),
        ),
    ]
