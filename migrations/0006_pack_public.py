# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-25 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0005_auto_20171124_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='pack',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
