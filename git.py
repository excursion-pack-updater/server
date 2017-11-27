from io import BytesIO
import os

from dulwich.client import get_transport_and_path
from dulwich.objects import Tree, Blob
from dulwich.repo import MemoryRepo
from dulwich.errors import HangupException

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

        print("Connecting to repository at", url)

        self.repo = MemoryRepo()
        self.client, self.path = get_transport_and_path(url)
        
        try:
            self.branches = self.client.fetch(self.path, self.repo, lambda refs: [], progress=_progress("fetch")).refs
        except HangupException as err:
            print("Failed to load repo `{}`: {}".format(url, err))
            
            return
        
        buffer = BytesIO()
        file, commit, abort = self.repo.object_store.add_pack()

        #TODO: support for different branches
        print("Loading repository")
        self.client.fetch_pack(self.path, lambda refs: [refs[b"HEAD"]], _GraphWalker(), pack_data=buffer.write, progress=_progress("pack"))
        buffer.seek(0)
        file.write(buffer.read())
        commit()
        print("Loading complete")

        self.objs = self.repo.object_store
        commit = self.objs[self.branches[b"HEAD"]]
        tree = self.objs[commit.tree]
        self.files = self.walk(tree) #TODO: break out into separate function

    def walk(self, tree, path=b""):
        files = {}

        for entry in tree.items():
            obj = self.objs[entry.sha]
            objType = type(obj)

            if objType is Tree:
                files.update(
                    self.walk(obj, os.path.join(path, entry.path))
                )
            elif objType is Blob:
                files[os.path.join(path, entry.path).decode("utf-8")] = entry.sha
            else:
                raise TypeError("Don't know what to do with {}.{}".format(objType.__module__, objType.__name__))

        return files

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

    for url in _repos.keys():
        if url in repoURLs:
            continue

        repo = _repos.pop(url)

        print("Closing repo", url)
        repo.repo.close()

    for dict in repoURLs:
        url = dict["gitURL"]

        if url in list(_repos.keys()):
            continue

        print("Opening repo", url, "for modpack", dict["name"])

        _repos[url] = Repository(url)

def get_repo(url):
    if url not in _repos:
        _repos[url] = Repository(url)

    return _repos[url]
