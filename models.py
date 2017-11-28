# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.db import models

class User(models.Model):
    base = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    apiKey = models.CharField(max_length=64)

class AuthKeys(models.Model):
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    expires = models.DateTimeField(auto_now=False, auto_now_add=False)

class Pack(models.Model):
    name = models.CharField(max_length=1024)
    slug = models.CharField(max_length=256)
    gitURL = models.CharField(max_length=1024)
    instanceZip = models.FileField(upload_to="epu/zips/")
    updaterBinaries = models.FileField(upload_to="epu/zips/")
    icon = models.FilePathField(path=os.path.join(settings.STATIC_ROOT, "epu/icons"), recursive=False, default="infinity.png")
    
    def __str__(self):
        return self.name
    
    def icon_filename(self):
        return self.icon.replace(settings.STATIC_ROOT, "")
