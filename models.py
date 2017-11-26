# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User as BaseUser

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
    changelist = models.FileField(upload_to="epu/changelists/", blank=True)
    
    def __str__(self):
        return self.name
