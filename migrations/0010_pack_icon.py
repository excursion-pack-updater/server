# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-27 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0009_auto_20171127_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='pack',
            name='icon',
            field=models.FilePathField(default='infinity.png', path='/home/steven/code-dump/django/static/epu/icons'),
        ),
    ]