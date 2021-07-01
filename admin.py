# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as BaseUser

from epu.models import User, UpdaterBins, Pack

@admin.register(UpdaterBins)
class UpdaterBinsAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "updated")

@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    class Media:
        js = ("epu/pack-admin.js",)

class UserInline(admin.StackedInline):
    model = User
    can_delete = False
    verbose_name_plural = "EPU Userdata"

class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)
    
admin.site.unregister(BaseUser)
admin.site.register(BaseUser, UserAdmin)
