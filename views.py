# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import hashlib
import time

from django.contrib.auth.models import User as BaseUser
from django.core.mail import send_mail
from django.http import *
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone

from .models import *

urlpatterns = []

class Render(object):
    def __init__(self, template, ctx={}, **responsekwargs):
        self.template = template
        self.ctx = ctx
        self.responsekwargs = responsekwargs

def route(pattern, **urlkwargs):
    from django.conf.urls import url
    from django.utils.decorators import available_attrs
    
    print(
        "route({!r}, {})".format(
            pattern,
            ", ".join(
                "{}={}".format(k, v) for k, v in urlkwargs.items()
            )
        )
    )
    
    def decorator(func):
        print("decorator called on", func.__qualname__)
        
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kwargs):
            print("route wrapper for", request.path, "calling", func.__qualname__)
            
            result = func(request, *args, **kwargs)
            
            if type(result) is Render:
                return render(request, result.template, result.ctx, **result.responsekwargs)
            else:
                return result
        
        urlpatterns.append(url(pattern, wrapper, **urlkwargs))
        
        return wrapper
    
    return decorator

@route(r"^generate_password/?$", name="generatePassword")
def generate_password(request):
    if not request.user.is_authenticated or not request.user.has_perm("auth.change_user"):
        return HttpResponseForbidden()
    
    password = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()
    
    return HttpResponse("blah\n" + password, content_type="text/plain")

@route(r"^login/(?P<key>[a-zA-Z0-9]+)?$", name="login")
def login(request, key):
    from bs4 import BeautifulSoup
    from django.contrib.auth import login
    
    if request.method == "GET":
        if not key:
            return Render("epu/login.html", {"title": "Log in"})
        
        ctx = {}
        authObj = None
        
        try:
            authObj = AuthKeys.objects.get(key__exact=key)
            
            if authObj.expires < timezone.now():
                raise AuthKeys.DoesNotExist
            
            login(request, authObj.user)
            
            return Render("epu/login.html", {"title": "Log in successful", "info": "You have logged in."})
        except AuthKeys.DoesNotExist:
            return Render("epu/login.html", {"title": "Log in failed", "error": "The authorization key is invalid (has it expired?)"})
        finally:
            if authObj:
                authObj.delete()
    elif request.method == "POST":
        '''import json
        
        return HttpResponse("post body:\n{}".format(json.dumps(request.POST, indent=4)), content_type="text/plain")'''
        email = request.POST.get("email", "")
        
        if email == "":
            return Render("epu/login.html", {"error": "No email supplied"})
        
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
        
        return Render(
            "epu/login.html",
            {
                "title": "Log in pending",
                "info": "An email has been sent to {} (if that email is registered). The link will expire after an hour.".format(email)
            }
        )
    else:
        return HttpResponseBadRequest()

@route(r"^logout/$", name="logout")
def logout(request):
    from django.contrib.auth import logout
    
    if request.user.is_authenticated:
        logout(request)
        return Render("epu/login.html", {"info": "You have logged out."})
    else:
        return Render("epu/login.html", {"error": "You are not logged in."})

@route(r"^pack/(?P<id>[0-9]+)", name="pack_detail")
def pack(request, id):
    pack = get_object_or_404(Pack, pk=id)
    
    return Render("epu/pack.html", {"pack": pack})

@route(r"^$", name="index")
def index(request):
    packs = list(Pack.objects.filter(public=True))
    
    if request.user.is_authenticated:
        try:
            user = User.objects.get(base=request.user)
            packs += user.allowedPacks.all()
        except User.DoesNotExist:
            pass
    
    ctx = {
        "packs": packs,
    }
    
    return Render("epu/index.html", ctx)
