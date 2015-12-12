# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0006_auto_20151211_0421'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlanceData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label_value', models.CharField(help_text=b'HTML displayed in the glance body.', max_length=1000)),
                ('lozenge_type', models.CharField(default=b'empty', max_length=10, choices=[(b'empty', b'no lozenge'), (b'default', b'default'), (b'success', b' success'), (b'current', b' current'), (b'complete', b'complete'), (b'error', b'error'), (b'new', b'new'), (b'moved', b'moved')])),
                ('lozenge_value', models.CharField(help_text=b'Text displayed inside the lozenge.', max_length=20, blank=True)),
                ('icon_url', models.URLField(help_text=b'URL to icon displayed on the right of the glance.', blank=True)),
                ('icon_url2', models.URLField(help_text=b'URL to hi-res icon displayed on the right of the glance.', blank=True)),
                ('metadata', models.TextField(help_text=b'Arbitrary JSON sent as the metadata value.', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='glance',
            name='data_url',
            field=models.URLField(help_text=b'REST endpoint exposed by the add-on for Glance data.', blank=True),
        ),
        migrations.AddField(
            model_name='glance',
            name='target',
            field=models.CharField(help_text=b'The key of a sidebar web panel, dialog or external page.', max_length=b'40', blank=True),
        ),
        migrations.AddField(
            model_name='glancedata',
            name='glance',
            field=models.ForeignKey(help_text=b'The Glance that this data updated.', to='hipchat.Glance'),
        ),
    ]
