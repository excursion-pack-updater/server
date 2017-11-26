# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-26 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0006_pack_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='pack',
            name='instanceZip',
            field=models.FileField(default='/dev/null', upload_to='epu/zips/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pack',
            name='slug',
            field=models.CharField(default='FIXME', max_length=256),
            preserve_default=False,
        ),
    ]
