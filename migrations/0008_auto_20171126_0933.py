# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-26 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0007_auto_20171126_0840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pack',
            name='public',
        ),
        migrations.RemoveField(
            model_name='user',
            name='allowedPacks',
        ),
        migrations.AddField(
            model_name='pack',
            name='changelist',
            field=models.FileField(blank=True, upload_to='epu/changelists/'),
        ),
    ]
