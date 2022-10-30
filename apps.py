# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig

class EpuConfig(AppConfig):
    name = "epu"
    verbose_name = "Excursion Pack Updater"
    default_auto_field = "django.db.models.AutoField"
    
    def ready(self):
        import sys
        
        from .git import update_repos
        
        #avoid running on manage.py commands, etc.
        isDevServer = len(sys.argv) > 1 and sys.argv[1] == "runserver"
        isProduction = len(sys.argv) == 1 #beware, your wsgi server may not behave as uwsgi
        
        if isDevServer or isProduction:
            update_repos()
