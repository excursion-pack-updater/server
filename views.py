# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import time

from django.contrib.auth.models import User as BaseUser
from django.core.mail import send_mail
from django.http import *
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .models import *

def generatePassword(request):
    if not request.user.is_authenticated or not request.user.has_perm("auth.change_user"):
        return HttpResponseForbidden()
    
    password = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()
    
    return HttpResponse("blah\n" + password, content_type="text/plain")

def login(request, key):
    from bs4 import BeautifulSoup
    
    if request.method == "GET":
        if not key:
            return render(request, "epu/login.html")
        
        ctx = {}
        
        try:
            authObj = AuthKeys.objects.get(key__exact=key)
            
            authObj.delete()
            
            if authObj.expires < timezone.now():
                raise AuthKeys.DoesNotExist
            
            return render(request, "epu/index.html", {"info": "You have logged in."})
        except AuthKeys.DoesNotExist:
            return render(request, "epu/login.html", {"error": "The authorization key is invalid (has it expired?)"})
        
    elif request.method == "POST":
        '''import json
        
        return HttpResponse("post body:\n{}".format(json.dumps(request.POST, indent=4)), content_type="text/plain")'''
        email = request.POST.get("email", "")
        
        if email == "":
            return render(request, "epu/login.html", {"error": "No email supplied"})
        
        try:
            user = BaseUser.objects.get(email__exact=email)
            key = hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()
            serverPort = request.META["SERVER_PORT"]
            body = get_template("epu/login_email.html").render(
                {
                    "email": email,
                    "firstName": user.first_name,
                    "url": "{}://{}{}".format(
                        request.scheme,
                        request.META["HTTP_HOST"],
                        reverse("epu:login", args=(key,))
                    ),
                    "time": timezone.now()
                }
            )
            
            AuthKeys.objects.create(
                user=user,
                key=key,
                expires=timezone.now() + timezone.timedelta(seconds=60 * 60),
            )
            send_mail(
                subject="EPU Login Link",
                from_email="epu@keladid.yoplitein.net",
                recipient_list=[user.email],
                message=BeautifulSoup(body, "html.parser").text,
                html_message=body,
            )
        except BaseUser.DoesNotExist:
            pass
        
        return render(request, "epu/login_pending.html", {"email": email})
    else:
        return HttpResponseBadRequest()

def logout(request):
    pass
