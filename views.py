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
from .git import update_repos, get_repo

update_repos()

urlpatterns = []

class Render(object):
    def __init__(self, template, ctx={}, **responsekwargs):
        self.template = template
        self.ctx = ctx
        self.responsekwargs = responsekwargs

def route(pattern, **urlkwargs):
    from django.conf.urls import url
    from django.utils.decorators import available_attrs
    
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            
            if type(result) is Render:
                return render(request, result.template, result.ctx, **result.responsekwargs)
            else:
                return result
        
        urlpatterns.append(url(pattern, wrapper, **urlkwargs))
        
        return wrapper
    
    return decorator

def renderForbidden():
    return Render("epu/index.html", {"title": "Forbidden", "error": "You must log in."}, status=403)

@route(r"^generate_password/?$", name="generatePassword")
def generate_password(request):
    if not request.user.is_authenticated or not request.user.has_perm("auth.change_user"):
        return renderForbidden()
    
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
        return Render("epu/login.html", {"title": "Logged out", "info": "You have logged out."})
    else:
        return Render("epu/login.html", {"title": "Log out failed", "error": "You are not logged in."})

@route(r"^pack/(?P<id>[0-9]+)/?$", name="pack_detail")
def pack(request, id):
    if not request.user.is_authenticated:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    
    return Render("epu/pack.html", {"pack": pack})

@route(r"^pack/(?P<id>[0-9]+)/instance/?", name="pack_instance")
def pack_instance(request, id):
    if not request.user.is_authenticated:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    response = HttpResponse(pack.instanceZip.read(), content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename={}-instance.zip".format(pack.slug)
    
    return response

@route(r"^pack/(?P<id>[0-9]+)/changelist/?", name="pack_changelist")
def pack_changelist(request, id):
    if not request.user.is_authenticated:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    
    return HttpResponseServerError()

@route(r"^pack/(?P<id>[0-9]+)/get/(?P<path>.*)$", name="pack_get")
def pack_get(request, id, path):
    from .git import get_repo
    
    if not request.user.is_authenticated:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    
    return HttpResponse(repo.read_file(path), content_type="application/octet-stream")

@route(r"^$", name="index")
def index(request):
    if not request.user.is_authenticated:
        return renderForbidden()
    
    return Render("epu/index.html", {"packs": Pack.objects.all()})
