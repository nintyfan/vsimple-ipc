#!/usr/bin/env python3

import signal
import stat, os


from errno import ENOENT

from fuse import FUSE, FuseOSError, Operations, fuse_get_context
from time import time

symlinks = {}

def for_int(number):
    return int(number)

def error(callback, params):
    try:
      return (false, callback(**params))
    except:
      return (true, None)

class Helper:
    def return_main_entries():
        output = []
        dirents2 = os.listdir('/proc')
        for r in dirents2:
          try:
            int(r)
            output.append(r + '-' + str(os.stat('/proc/' + r).st_ctime))
          except ValueError:
            output.append(r)
        return output

class Guard(Operations):
    def __init__(self):
        self.helper = Helper()
    
    def check_rights(self):
      uid, gid, pid = fuse_get_context()
      if uid != self.uid:
        raise FuseOSError(errno.EACCES)
    # Helpers
    # =======

    def _full_path(self, partial):
        if partial.startswith("/"):
            partial = partial[1:]
        path = os.path.join(self.root, partial)
        return path

    # Filesystem methods
    # ==================
    def getattr(self, path, fh=None):
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        ok = False
        if len(path_parts) == 0:
            ok = True
        else:
            if path_parts[0] in symlinks:
               ok = True
            elif not( path_parts[0] in Helper.return_main_entries()):
               pass
            else:
                ok = True
        if ok:
          return {'st_atime': int(time()), 'st_ctime': int(time()), 'st_gid': 0, 'st_mode': (stat.S_IFDIR | 0o755), 'st_mtime': int(time()), 'st_uid': 0}
        else:
          raise FuseOSError(ENOENT)

    def readlink(self, path):
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        
        if len(path_parts) > 1:
            return symlink[path_parts[0]]['app']
    
    def readdir(self, path, fh):
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        dirents = ['.', '..']
        output=[]
        print(path_parts)
        if len(path_parts) == 0:
           output.extend(Helper.return_main_entries())
        else:
           if path_parts[0] in symlinks:
               output.extend(symlinks[path_parts[0]].keys())
           elif not( path_parts[0] in Helper.return_main_entries()):
               raise FuseOSError(ENOENT)
        output.extend(dirents)
        return output

    def symlink(self, name, target):
        uid, gid, pid = fuse_get_context()
        symlinks[str(pid) + '-' + str(os.stat('/proc/' + str(pid)).st_ctime)] = { 'app': target }
    
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

if __name__ == '__main__':
  FUSE(Guard(), '/vsimple-ipc', nothreads=True, foreground=True, **{'allow_other': True})
