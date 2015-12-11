# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hipchat', '0005_auto_20151211_0417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glance',
            name='app',
            field=models.ForeignKey(related_name='glances', to='hipchat.HipChatApp', help_text=b'The app this glance belongs to.'),
        ),
    ]
