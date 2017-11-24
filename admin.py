# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as BaseUser

from epu.models import User, Pack

models = (
    Pack,
)

for model in models:
    admin.site.register(model)

class UserInline(admin.StackedInline):
    model = User
    can_delete = False
    verbose_name_plural = "EPU Userdata"

class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)
    
    class Media:
        js = () #("epu/user-admin.js",)
    
admin.site.unregister(BaseUser)
admin.site.register(BaseUser, UserAdmin)
