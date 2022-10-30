# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.conf import settings
from django.contrib.auth.models import User as BaseUser
from django.db import models

class User(models.Model):
    base = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    apiKey = models.CharField(max_length=64, blank=True, verbose_name="API key", help_text="Leave blank to regenerate.")
    
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

class UpdaterBins(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=160, help_text="Use to record e.g. the git tag+hash the zips were built from.")
    winZip = models.FileField(upload_to="epu/zips/", verbose_name="Windows zip")
    macZip = models.FileField(upload_to="epu/zips/", verbose_name="macOS zip")
    linuxZip = models.FileField(upload_to="epu/zips/", verbose_name="Linux zip")
    
    class Meta:
        verbose_name = "Client Binary"
        verbose_name_plural = "Client Binaries"
    
    def __str__(self):
        return "Binaries created {} ({})".format(self.created.strftime("%Y-%m-%d/%H:%M"), self.description)
    
    def save(self, *args, **kwargs):
        try:
            old = UpdaterBins.objects.get(id=self.id)
            
            if old.winZip != self.winZip:
                os.remove(old.winZip.path)
            
            if old.macZip != self.macZip:
                os.remove(old.macZip.path)
            
            if old.linuxZip != self.linuxZip:
                os.remove(old.linuxZip.path)
        except UpdaterBins.DoesNotExist:
            pass
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        os.remove(self.winZip.path)
        os.remove(self.macZip.path)
        os.remove(self.linuxZip.path)
        
        super().delete(*args, **kwargs)

class Pack(models.Model):
    name = models.CharField(max_length=1024, verbose_name="Display name")
    slug = models.CharField(max_length=256, verbose_name="URL-friendly name")
    gitURL = models.CharField(max_length=1024, verbose_name="Git repository")
    instanceZip = models.FileField(upload_to="epu/zips/", verbose_name="Instance zip")
    updaterBinaries = models.ForeignKey(UpdaterBins, null=True, on_delete=models.SET_NULL, verbose_name="Client binaries")
    icon = models.FilePathField(path=os.path.join(settings.STATIC_ROOT, "epu/icons"), recursive=False, default="infinity.png")
    
    def __str__(self):
        return self.name
    
    def icon_filename(self):
        return self.icon.replace(settings.STATIC_ROOT, "")
    
    def save(self, *args, **kwargs):
        try:
            old = Pack.objects.get(id=self.id)
            
            if old.instanceZip != self.instanceZip:
                os.remove(old.instanceZip.path)
        except Pack.DoesNotExist:
            pass
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        os.remove(self.instanceZip.path)
        
        super().delete(*args, **kwargs)
