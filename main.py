#!/usr/bin/env python3

# Copyright (c) 2022 Sławomir Lach <slawek@lach.art.pl>
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import signal
import stat, os


from errno import ENOENT, EACCES

from fuse import FUSE, FuseOSError, Operations, fuse_get_context
from time import time


# Custom import
import monitor
from helper import Helper

symlinks = {}

def for_int(number):
    return int(number)

def error(callback, params):
    try:
      return (false, callback(**params))
    except:
      return (true, None)


class Guard(Operations):
    def __init__(self):
        self.helper = Helper()
        self.inotify = None
    
    def real_init(self):
        if None == self.inotify:
            self.inotify = monitor.watcher()
            self.inotify.start()
    
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
        uid = 0
        gid = 0
        mode = (stat.S_IFDIR | 0o755)
        path_parts = []
        uid, gid, pid = fuse_get_context()
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
            ok = True
            if not( path_parts[0] in Helper.return_main_entries()):
               ok = False
            if len(path_parts) > 1 and (not path_parts[0] in symlinks or not(path_parts[1] in symlinks[path_parts[0]])):
               ok = False
        if len(path_parts) > 1 and path_parts[0] in symlinks and path_parts[1] in symlinks[path_parts[0]]:
            mode = (stat.S_IFLNK | 0o755)
        if len(path_parts) > 1:
            uid, gid = Helper.get_process_rights(int(path_parts[0].split('-')[0]))
        if ok:
          return {'st_atime': int(time()), 'st_ctime': int(time()), 'st_gid': gid, 'st_mode': mode, 'st_mtime': int(time()), 'st_uid': uid}
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
            self.real_init()
            self.inotify.add_path(path)
        return symlinks[path_parts[0]]['app']
    
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
        if len(path_parts) == 0:
            output.extend(Helper.return_main_entries())
        else:
           if path_parts[0] in symlinks:
               output.extend(symlinks[path_parts[0]].keys())
           elif not( path_parts[0] in Helper.return_main_entries()):
               raise FuseOSError(ENOENT)
               output.extend(dirents)
        return output
    
    def open(self, path, flags):
        self.real_init()
        self.inotify.add_path(path)
        return os.open(path, flags)

    def symlink(self, name, target):
        path = name
        uid, gid, pid = fuse_get_context()
        process_name = str(pid) + '-' + Helper.get_creation_time(pid)
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        if len(path_parts) < 2:
            raise FuseOSError(EACCES)
        
        if process_name != path_parts[0] or "app" != path_parts[1]:
            raise FuseOSError(EACCES)
        
        symlinks[process_name] = { 'app': target }
    
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
