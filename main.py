#!/usr/bin/env python3

import signal
import stat, os


from errno import ENOENT, EACCES

from fuse import FUSE, FuseOSError, Operations, fuse_get_context
from time import time


# Custom import
import monitor
import stateDir

Dir = stateDir.Directory
File = stateDir.File

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
                  line = a.split(':')[1]
                  uid = int(line.split()[0])
         
         pstat = open('/proc/' + str(pid) + '/status', 'r')
         lines = pstat.readlines()
         for a in lines:
              if a.startswith('Gid:'):
                  a = Helper.remove_white(a)
                  line = a.split(':')[1]
                  gid = int(line.split()[0])
         
         return uid,gid

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
        
        if len(path_parts) == 0:
            return
        if path_parts[0] == '':
            del path_parts[0]
        print("A")
        print(path_parts)
        print("B")
        ok = False
        if len(path_parts) == 0:
            ok = True
        else:
            ok = True
            if not( path_parts[0] in Helper.return_main_entries()):
               ok = False
            if len(path_parts) > 1 and (not path_parts[0] in symlinks or not(path_parts[1] in symlinks[path_parts[0]])):
               ok = False
        if len(path_parts) > 1 and path_parts[1] == 'state':
            # read from DIR -> File classes
            if not path_parts[0] in symlinks:
                raise FuseOSError(ENOENT)
            status = symlinks[path_parts[0]]['state']
            print(status.__class__)
            if path_parts[0].startswith(str(pid)):
                mode = (stat.S_IFDIR | 0o755)
                return {'st_atime': int(time()), 'st_ctime': int(time()), 'st_gid': gid, 'st_mode': mode, 'st_mtime': int(time()), 'st_uid': uid}
            if status is stateDir.Directory:
              mode = (stat.S_IFDIR | 0o777)
            else:
              mode = (stat.S_IFDIR | status.getRights())
            uid, gid, pid = fuse_get_context()
            if len(path_parts) > 2:
                   i = 0
                   for item in path_parts:
                       if item == '..':
                           i = i - 1
                           if i < 0:
                               raise FuseOSError(ENOENT)
                       else:
                            i = i + 1
                   pid = path_parts[0]
                   del path_parts[0]
                   del path_parts[0]
                   print('0')
                   print(path_parts)  
                   print('1')
                   print(stateDir.state_dir_path + '/' + pid + '/' +  '/'.join(path_parts))
                   stat_ = os.lstat(stateDir.state_dir_path + pid + '/' + '/'.join(path_parts))
                   return {'st_atime': stat_.st_atime, 'st_ctime': stat_.st_ctime, 'st_gid': gid, 'st_mode': stat_.st_mode, 'st_mtime': stat_.st_mtime, 'st_uid': uid}
            #item = status.getFile(path_parts[2])
        elif len(path_parts) > 1 and path_parts[0] in symlinks and path_parts[1] in symlinks[path_parts[0]]:
            if path_parts[1] == 'app':
              mode = (stat.S_IFLNK | 0o755)
            elif path_parts[1] == 'state':
              mode = (stat.S_IFDIR | 0o755)
        
        # Obaining UID and GID
        if len(path_parts) > 1:
            try:
              uid, gid = Helper.get_process_rights(int(path_parts[0].split('-')[0]))
            except ValueError:
              pass
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
            return symlinks[path_parts[0]]['app']
    
    def readdir(self, path, fh):
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
        if path_parts[0] == '':
            del path_parts[0]
        dirents = ['.', '..']
        output=[]
        print('a')
        print(path)
        print(path_parts)
        if len(path_parts) == 0:
           output.extend(Helper.return_main_entries())
        else:
           if path_parts[0] in symlinks:
               if len(path_parts) > 1 : print(path_parts[1])
               if len(path_parts) > 1 and path_parts[1] == 'state':
                   # Attention! This is insecure
                   i = 0
                   for item in path_parts:
                       if item == '..':
                           i = i - 1
                           if i < 0:
                               raise FuseOSError(ENOENT)
                       else:
                            i = i + 1
                   pid = path_parts[0]
                   del path_parts[0]
                   del path_parts[0]
                   print(path_parts)
                   print(stateDir.state_dir_path + '/' + pid + '/' +  '/'.join(path_parts))
                   output.extend(os.listdir(stateDir.state_dir_path + '/' + pid + '/'  + '/'.join(path_parts)))
               else:
                   items = list(symlinks[path_parts[0]].keys())
                   items.remove('meta')
                   items.remove('state')
                   output.extend(items)
                   output.extend(['state'])
           elif not( path_parts[0] in Helper.return_main_entries()):
               raise FuseOSError(ENOENT)
        output.extend(dirents)
        return output
    
    def open(self, path, flags):
        #self.real_init()
        #self.inotify.add_path(path)
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        if File.checkRights(symlinks, path_parts, fuse_get_context()[2], flags):
            symlinks[path_parts[0]]['meta'].ocount += 1
                   
        return os.open(path, flags)
    
    def release(self, path, fh):
        path_parts = []
        if '/' == path:
            path_parts = []
        else:
            path_parts = path.split('/')
            if '/' == path[0]:
                del path_parts[0]
        
        if path_parts[1] == 'state':
            symlinks[path_parts[0]]['meta'].ocount -=1
            
            if symlinks[path_parts[0]]['meta'].ocount == 0:
                token = path_parts[0].split('-')
                time = Helper.get_creation_time(int(token[0]))
                if time != token[1]:
                    # Delete stateDir
                    symlinks[path_parts[0]]['state'].delete()
                #close file
                os.close(fh)
        

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
        
        symlinks[process_name] = { 'app': target, 'meta': stateDir.MetaInfo(), 'state': stateDir.Dir(stateDir.state_dir_path + '/' + path_parts[0]) }
    
    access = None
    flush = None
    getxattr = None
    listxattr = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

if __name__ == '__main__':
  FUSE(Guard(), '/vsimple-ipc', nothreads=True, foreground=True, **{'allow_other': True})
