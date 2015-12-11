# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0004_auto_20151210_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Glance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(help_text=b'Unique key (in the context of the integration) to identify this glance.', max_length=40)),
                ('name', models.CharField(help_text=b'The display name of the glance.', max_length=100, blank=True)),
                ('app', models.ForeignKey(help_text=b'The app this glance belongs to.', to='hipchat.HipChatApp')),
            ],
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='created_at',
            field=models.DateTimeField(help_text=b'Set when this object is first saved.'),
        ),
    ]
