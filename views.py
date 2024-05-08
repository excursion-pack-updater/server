# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import hashlib
import json
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
    from django.urls import re_path
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            
            if type(result) is Render:
                return render(request, result.template, result.ctx, **result.responsekwargs)
            else:
                return result
        
        urlpatterns.append(re_path(pattern, wrapper, **urlkwargs))
        
        return wrapper
    
    return decorator

def renderUnauthenticated():
    return Render("epu/index.html", {"title": "Please log in", "error": "You must log in to access this page."}, status=401)

def renderUnauthorized():
    return Render("epu/index.html", {"title": "Forbidden", "error": "You do not have permission to access this page."}, status=403)

def valid_api_key(request, allowQuery = False):
    key = request.META.get("HTTP_X_EPU_KEY", None)
    
    if not key and allowQuery:
        key = request.GET.get("apikey", None)
    
    if not key:
        return None
    
    try:
        user = User.objects.get(apiKey=key)
        if not user.base.is_active:
            return None
        return user
    except User.DoesNotExist:
        return None

@route(r"^login/(?P<key>[a-zA-Z0-9]+)?$", name="login")
def login(request, key = None):
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
            if not user.is_active:
                raise BaseUser.DoesNotExist
            
            key = hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()
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

@route(r"^pack/(?P<id>[0-9]+)/$", name="pack_detail")
def pack(request, id):
    if not request.user.is_authenticated:
        return renderUnauthenticated()
    
    pack = get_object_or_404(Pack, pk=id)
    
    return Render("epu/pack.html", {"pack": pack, "epuUser": User.objects.get(base=request.user)})

@route(r"^pack/(?P<id>[0-9]+)/instance/(?P<platform>[a-zA-Z0-9]+)/?$", name="pack_instance")
def pack_instance(request, id, platform):
    from io import BytesIO
    from zipfile import ZipFile, ZipInfo
    from stat import S_IFREG
    import os
    
    if not request.user.is_authenticated:
        return renderUnauthenticated()
    
    if not platform in ["win", "mac", "linux"]:
        return Render("epu/index.html", {"title": "Error", "error": "Unknown platform"}, status = 400)
    
    pack = get_object_or_404(Pack, pk=id)
    bins = pack.updaterBinaries
    user = User.objects.get(base__pk=request.user.id)
    outBuffer = BytesIO()
    binariesZip = None
    
    if platform == "win":
        binariesZip = bins.winZip
    elif platform == "mac":
        binariesZip = bins.macZip
    elif platform == "linux":
        binariesZip = bins.linuxZip
    else:
        print("this should be impossible? id {} plat `{}`".format(id, platform))
        return HttpResponseServerError()
    
    with ZipFile(outBuffer, "w") as zip:
        instanceBuffer = BytesIO(pack.instanceZip.read())
        instanceCfg = {}
        
        with ZipFile(instanceBuffer, "r") as instanceZip:
            for info in instanceZip.infolist():
                if info.file_size <= 0:
                    continue
                
                if info.filename == "instance.cfg":
                    with instanceZip.open("instance.cfg", "r") as f:
                        for line in f:
                            line = line.decode("utf-8").strip()
                            key, value = line.split("=", 1)
                            instanceCfg[key] = value
                    
                    continue
                
                with instanceZip.open(info.filename, "r") as src:
                    with zip.open(os.path.join(pack.slug, info.filename), "w") as dest:
                        dest.write(src.read())
        
        instanceCfg["InstanceType"] = "OneSix"
        instanceCfg["MCLaunchMethod"] = "LauncherPart"
        instanceCfg["OverrideCommands"] = "true"
        instanceCfg["PreLaunchCommand"] = '"$INST_DIR/epu_client{}"'.format(".exe" if platform == "win" else "")
        instanceCfg["name"] = pack.name
        instanceCfg["iconKey"] = os.path.splitext(os.path.basename(pack.icon))[0]
        
        with zip.open(os.path.join(pack.slug, "instance.cfg"), "w") as f:
            for k, v in instanceCfg.items():
                f.write("{}={}\n".format(k, v).encode("utf-8"))
        
        binariesBuffer = BytesIO(binariesZip.read())
        with ZipFile(binariesBuffer, "r") as binariesZip:
            for info in binariesZip.infolist():
                if info.file_size <= 0:
                    continue
                
                newinfo = ZipInfo(os.path.join(pack.slug, info.filename))
                if platform != "win" and not info.filename.endswith(".txt"):
                    # on unixen mark binaries as normal files (S_IFREG) with u+rwx,g+r,o+r
                    newinfo.external_attr = (0o744 | S_IFREG) << 16
                
                with binariesZip.open(info.filename, "r") as src:
                    with zip.open(newinfo, "w") as dest:
                        dest.write(src.read())
        
        with zip.open(os.path.join(pack.slug, ".minecraft", "epu_client.json"), "w") as f:
            config = {
                "backendUrl": f"{request.scheme}://{request.META['HTTP_HOST']}{reverse('epu:index')}",
                "packId": str(pack.id),
                "apiKey": user.apiKey,
            }
            # cannot dump to file directly -- `ZipWriteFile.write` doesn't accept `str`
            f.write(json.dumps(config, indent="\t").encode("utf-8"))
    
    response = HttpResponse(outBuffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f"attachment; filename={pack.slug}-{platform}.zip"
    return response

@route(r"^pack/(?P<id>[0-9]+)/version/?$", name="pack_version")
def pack_version(request, id):
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderUnauthorized()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    head = repo.get_head_commit()
    sha = repo.get_commit_sha(head).decode("utf-8")
    
    return HttpResponse(sha, content_type="text/plain")

@route(r"^pack/(?P<id>[0-9]+)/changelist/(?P<commitSHA>[a-fA-F0-9]{40})?$", name="pack_changelist")
def pack_changelist(request, id, commitSHA = ""):
    from dulwich.diff_tree import tree_changes
    
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderUnauthorized()
    
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
        "hashes": repo.hashes,
    }
    changes = tree_changes(repo.objs, baseTreeSHA, head.tree)
    
    for change in changes:
        if change.type == "add" or change.type == "modify":
            if change.type == "modify":
                assert change.old.path == change.new.path, "old.path != new.path, don't know what to do!"
            
            changelist["download"].append(change.new.path.decode("utf-8"))
        elif change.type == "delete":
            changelist["delete"].append(change.old.path.decode("utf-8"))
    
    return JsonResponse(changelist, json_dumps_params={"indent": "\t"})

@route(r"^pack/(?P<id>[0-9]+)/get/(?P<path>.*)$", name="pack_get")
def pack_get(request, id, path):
    import urllib
    
    from .git import get_repo
    
    if not request.user.is_authenticated and not valid_api_key(request):
        return renderUnauthorized()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = get_repo(pack.gitURL)
    
    return HttpResponse(repo.read_file(urllib.parse.unquote(path)), content_type="application/octet-stream")

@route(r"^pack/(?P<id>[0-9]+)/reload", name="pack_reload")
def pack_reload(request, id):
    from .git import reload_repo
    
    if not request.user.is_authenticated:
        user = valid_api_key(request, True)
        if not user or not user.base.is_staff: return renderUnauthorized()
    
    pack = get_object_or_404(Pack, pk=id)
    repo = reload_repo(pack.gitURL)
    
    return Render("epu/pack.html", {"info": "Repository reloaded.", "pack": pack})

@route(r"reload_packs/", name="pack_reload_all")
def pack_reload_all(request):
    from . import git
    
    if not request.user.is_authenticated: return renderUnauthenticated()
    if not request.user.is_staff: return renderUnauthorized()
    
    git.update_repos()
    return HttpResponseRedirect(reverse("epu:repo_status") + "?reloaded")

@route(r"howto/?", name="howto")
def howto(request):
    #FIXME: cache
    import markdown
    from django.contrib.staticfiles.finders import find
    
    src = ""
    path = find("epu/howto.md")
    
    with open(path, "r") as f:
        src = f.read()
    
    return Render(
        "epu/base.html",
        {
            "title": "How to use MultiMC",
            "body": markdown.markdown(src),
        }
    )

@route(r"repo_status/?", name="repo_status")
def repo_status(request):
    import time
    from . import git
    
    if not request.user.is_authenticated: return renderUnauthenticated()
    if not request.user.is_staff: return renderUnauthorized()
    
    now = timezone.now()
    def massage_repo(pair):
        url, repo = pair
        if repo.failed:
            info = {
                "failed": True,
                "updated": repo.updated,
                "log": repo.errlog,
            }
            return (url, info)
        
        msg = repo.get_head_msg()
        if len(msg) > 40:
            msg = msg[0:40].strip() + ".."
        
        info = {
            "failed": False,
            "updated": repo.updated,
            "head": repo.get_head_sha(),
            "headText": msg,
        }
        return (url, info)
    
    ctx = {"repos": dict(map(massage_repo, git._repos.items()))}
    if "reloaded" in request.GET:
        ctx["info"] = "Repositories reloaded."
    return Render("epu/status.html", ctx)

@route(r"^$", name="index")
def index(request):
    if not request.user.is_authenticated:
        return renderUnauthenticated()
    
    return Render("epu/index.html", {"packs": Pack.objects.all()})
