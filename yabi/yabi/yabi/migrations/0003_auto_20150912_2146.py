# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yabi', '0002_load_quickstart_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tool',
            options={'ordering': ('desc__name', 'backend__name')},
        ),
    ]
