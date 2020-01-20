# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('languages_plus', '0002_auto_20141008_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='countries_spoken',
            field=models.ManyToManyField(blank=True, to='countries_plus.Country'),
        ),
    ]
