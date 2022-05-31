#!/usr/bin/env python3

import signal
import stat, os


from errno import ENOENT, EACCES

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
            output.append(r + '-' + str(Helper.get_creation_time(int(r))))
          except ValueError:
            output.append(r)
        return output
    def get_creation_time(pid):
         pstat = open('/proc/' + str(pid) + '/stat', 'r')
         line = pstat.readlines()[0]
         return line.split(' ')[23]
    def remove_white(string):
        result = ''
        was_space=False
        for a in range(0,len(string)-1):
            if string[a].isspace():
                if not(was_space):
                    result += string[a]
                was_space = True
            else:
                was_space = False
                result += string[a]
        return result
                
    def get_process_rights(pid):
         uid = None
         gid = None
         
         pstat = open('/proc/' + str(pid) + '/status', 'r')
         lines = pstat.readlines()
         for a in lines:
              if a.startswith('Uid:'):
                  a = Helper.remove_white(a)
                  print(a)
                  line = a.split(':')[1]
                  uid = int(line.split()[0])
         
         pstat = open('/proc/' + str(pid) + '/status', 'r')
         lines = pstat.readlines()
         for a in lines:
              if a.startswith('Gid:'):
                  a = Helper.remove_white(a)
                  print(a)
                  line = a.split(':')[1]
                  gid = int(line.split()[0])
         
         return uid,gid

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
        print(path_parts)
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
        print(path_parts[0])
        print(symlinks[path_parts[0]])
        if len(path_parts) > 1:
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
        print(path_parts)
        if len(path_parts) == 0:
           output.extend(Helper.return_main_entries())
        else:
           if path_parts[0] in symlinks:
               output.extend(symlinks[path_parts[0]].keys())
           elif not( path_parts[0] in Helper.return_main_entries()):
               raise FuseOSError(ENOENT)
        print(symlinks)
        output.extend(dirents)
        return output

    def symlink(self, name, target):
        path = name
        uid, gid, pid = fuse_get_context()
        process_name = str(pid) + '-' + Helper.get_creation_time(pid)
        path_parts = []
        print("process_name")
        print(process_name)
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        if len(path_parts) < 2:
            print("A")
            raise FuseOSError(EACCES)
        
        if process_name != path_parts[0] or "app" != path_parts[1]:
            print("B")
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
