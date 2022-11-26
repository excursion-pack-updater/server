from io import BytesIO
import os

from django.utils import timezone
from dulwich.client import get_transport_and_path
from dulwich.objects import Tree, Blob
from dulwich.repo import MemoryRepo

_repos = {}

class _GraphWalker(object):
    def ack(self, sha):
        pass

    def next(self):
        pass

    def __next__(self):
        pass

class Repository(object):
    def __init__(self, url):
        self.url = url
        self.updated = timezone.now()
        self.failed = True
        self.errlog = "No log available"

        print("Connecting to repository at", url)

        self.repo = MemoryRepo()
        self.client, self.path = get_transport_and_path(url)
        
        try:
            self.branches = self.client.fetch(self.path, self.repo, lambda refs: [], progress=_progress("fetch")).refs
            
            buffer = BytesIO()
            file, commit, abort = self.repo.object_store.add_pack()

            #TODO: support for different branches
            print("Loading repository {}".format(url))
            self.client.fetch_pack(self.path, lambda refs: [refs[b"HEAD"]], _GraphWalker(), pack_data=buffer.write, progress=_progress("pack"))
            buffer.seek(0)
            file.write(buffer.read())
            commit()
            print("Loading complete for repository {}".format(url))

            self.objs = self.repo.object_store
            commit = self.objs[self.branches[b"HEAD"]]
            tree = self.objs[commit.tree]
            self.files, self.hashes = self.walk(tree)
            
            self.failed = False
        except Exception as err:
            import traceback
        
            print("Failed to load repo `{}`: {}".format(url, err))
            self.errlog = "{}: {}\n\n{}".format(type(err).__name__, err, traceback.format_exc())
            
            return
    
    def walk(self, tree, path=b""):
        from hashlib import sha1
        files = {}
        hashes = {}

        for entry in tree.items():
            obj = self.objs[entry.sha]
            objType = type(obj)

            if objType is Tree:
                data = self.walk(obj, os.path.join(path, entry.path))
                files.update(data[0])
                hashes.update(data[1])
            elif objType is Blob:
                # import pdb; pdb.set_trace()
                fpath = os.path.join(path, entry.path).decode("utf-8")
                files[fpath] = entry.sha
                hashes[fpath] = sha1(self.objs[entry.sha].as_raw_string()).hexdigest()
            else:
                raise TypeError("Don't know what to do with {}.{}".format(objType.__module__, objType.__name__))
        
        return files, hashes

    def read_file(self, path):
        "Returns file contents as bytestring."

        return self.objs[self.files[path]].as_raw_string()
    
    def get_commit(self, sha):
        return self.objs[sha]
    
    def get_head_commit(self):
        return self.get_commit(self.branches[b"HEAD"])
    
    def get_root_commit(self):
        commit = self.get_head_commit()
        
        while len(commit.parents) > 0:
            commit = self.objs[commit.parents[0]]
        
        return commit
    
    def get_commit_sha(self, commit):
        return commit.sha().hexdigest().encode("utf-8")
    
    def get_head_sha(self):
        return self.branches[b"HEAD"].decode("utf-8")
    
    def get_head_msg(self):
        return self.get_head_commit().message.decode("utf-8")

def _progress(prefix):
    def func(msg):
        print(prefix, ": ", msg.decode("utf-8"), sep="", end="")
    
    return func

def update_repos():
    from .models import Pack

    repoURLs = (Pack
        .objects
        .order_by()
        .values("gitURL", "name")
        .distinct()
    )

    for url in list(_repos.keys()):
        if url in repoURLs:
            continue
        
        print("Deleting repo", url)
        _repos.pop(url)
    
    for dict in repoURLs:
        url = dict["gitURL"]
        if url in _repos:
            continue
        
        print("Opening repo", url, "for modpack", dict["name"])
        _repos[url] = Repository(url)

def get_repo(url):
    if url not in _repos:
        _repos[url] = Repository(url)

    return _repos[url]

def reload_repo(url):
    if url in _repos:
        _repos.pop(url)
    
    return get_repo(url)
