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
from .git import get_repo

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

def valid_api_key(request):
    key = request.META.get("HTTP_X_EPU_KEY", None)
    
    if not key:
        return None
    
    try:
        return User.objects.get(apiKey=key)
    except User.DoesNotExist:
        return None

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

@route(r"^pack/(?P<id>[0-9]+)/instance/?$", name="pack_instance")
def pack_instance(request, id):
    from io import BytesIO
    from zipfile import ZipFile
    import os
    
    if not request.user.is_authenticated:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    user = User.objects.get(base__pk=request.user.id)
    outBuffer = BytesIO()
    
    with ZipFile(outBuffer, "w") as zip:
        instanceBuffer = BytesIO(pack.instanceZip.read())
        
        with ZipFile(instanceBuffer, "r") as instanceZip:
            for info in instanceZip.infolist():
                if info.file_size <= 0:
                    continue
                
                if info.filename == "instance.cfg":
                    instanceCfg = {}
                    
                    with instanceZip.open("instance.cfg", "r") as f:
                        for line in f:
                            line = line.decode("utf-8").strip()
                            key, value = line.split("=", 1)
                            instanceCfg[key] = value
                    
                    instanceCfg["OverrideCommands"] = "true"
                    instanceCfg["PreLaunchCommand"] = "CMD /C $INST_DIR/pack_sync.exe" #FIXME: hardcoded to Windows
                    instanceCfg["iconKey"] = os.path.splitext(os.path.basename(pack.icon))[0]
                    
                    with zip.open("instance.cfg", "w") as f:
                        for k, v in instanceCfg.items():
                            f.write("{}={}\n".format(k, v).encode("utf-8"))
                    
                    continue
                
                with instanceZip.open(info.filename, "r") as src:
                    with zip.open(info.filename, "w") as dest:
                        dest.write(src.read())
        
        binariesBuffer = BytesIO(pack.updaterBinaries.read())
        
        with ZipFile(binariesBuffer, "r") as binariesZip:
            for info in binariesZip.infolist():
                if info.file_size <= 0:
                    continue
                
                with binariesZip.open(info.filename, "r") as src:
                    with zip.open(info.filename, "w") as dest:
                        dest.write(src.read())
        
        with zip.open("minecraft/pack_sync.ini", "w") as f:
            f.write(
                "backendURL={}://{}{}\n".format(
                    request.scheme,
                    request.META["HTTP_HOST"],
                    reverse("epu:index")
                ).encode("utf-8"),
            )
            f.write("packID={}\n".format(pack.id).encode("utf-8"))
            f.write("apiKey={}\n".format(user.apiKey).encode("utf-8"))
    
    response = HttpResponse(outBuffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename={}-instance.zip".format(pack.slug)
    
    return response

@route(r"^pack/(?P<id>[0-9]+)/version/?$", name="pack_version")
def pack_version(request, id):
    import json
    
    from dulwich.diff_tree import tree_changes
    
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    head = repo.get_head_commit()
    sha = repo.get_commit_sha(head).decode("utf-8")
    
    return HttpResponse(sha, content_type="text/plain")

@route(r"^pack/(?P<id>[0-9]+)/changelist/(?P<commitSHA>[a-zA-Z0-9]{40})?$", name="pack_changelist")
def pack_changelist(request, id, commitSHA):
    import json
    
    from dulwich.diff_tree import tree_changes
    
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    head = repo.get_head_commit()
    
    if commitSHA:
        baseTreeSHA = repo.get_commit(commitSHA.encode("utf-8")).tree
    else:
        baseTreeSHA = b""
    
    changelist = {
        "download": [],
        "delete": [],
    }
    changes = tree_changes(repo.objs, baseTreeSHA, head.tree)
    
    for change in changes:
        if change.type == "add" or change.type == "modify":
            if change.type == "modify":
                assert change.old.path == change.new.path, "old.path != new.path, don't know what to do!"
            
            changelist["download"].append(change.new.path.decode("utf-8"))
        elif change.type == "delete":
            changelist["delete"].append(change.old.path.decode("utf-8"))
    
    return HttpResponse(json.dumps(changelist), content_type="application/json")

@route(r"^pack/(?P<id>[0-9]+)/get/(?P<path>.*)$", name="pack_get")
def pack_get(request, id, path):
    import urllib
    
    from .git import get_repo
    
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    
    return HttpResponse(repo.read_file(urllib.parse.unquote(path)), content_type="application/octet-stream")

@route(r"^pack/(?P<id>[0-9]+)/reload", name="pack_reload")
def pack_reload(request, id):
    from .git import reload_repo
    
    if not request.user.is_authenticated and not valid_api_key(request).base.is_staff:
        return renderForbidden()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = reload_repo(pack.gitURL)
    
    return Render("epu/pack.html", {"info": "Repository reloaded.", "pack": pack})

@route(r"^$", name="index")
def index(request):
    if not request.user.is_authenticated:
        return renderForbidden()
    
    return Render("epu/index.html", {"packs": Pack.objects.all()})
