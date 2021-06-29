# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.db import models

class User(models.Model):
    base = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    apiKey = models.CharField(max_length=64, blank=True)
    
    def save(self, *args, **kwargs):
        import hashlib
        import time
        
        if self.apiKey == "":
            now = time.ctime().encode()
            self.apiKey = hashlib.sha256(now).hexdigest()
        
        super().save(*args, **kwargs)

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
    
    def save(self, *args, **kwargs):
        import os
        
        try:
            old = Pack.objects.get(id=self.id)
            
            if old.instanceZip != self.instanceZip:
                os.remove(old.instanceZip.path)
            
            if old.updaterBinaries != self.updaterBinaries:
                os.remove(old.updaterBinaries.path)
        except Pack.DoesNotExist:
            pass
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        import os
        
        os.remove(self.instanceZip.path)
        os.remove(self.updaterBinaries.path)
        
        super().delete(*args, **kwargs)
