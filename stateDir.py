import os


state_dir_path = '/run/lib/vsimple-ipc/storage/'

class Rights:
  def __init__(self):
    self.unixRights = 0o777
  def getRights(self):
    return self.unixRights
  def setRights(self,rights):
    self.unixRights = rights
  def checkRights(symlinks, path_parts, pid, mode):
    if len(path_parts) > 1 and path_parts[1] == 'status':
      if path_parts[0].startsWith(str(pid)):
        return True
      status = symlinks[path_parts[0]]['status']
      i = 1
      for a in range(1, len(path_parts) - 1):
        status = status.getFile(path_parts[i])
      if status.getRights() & mode == mode:
        return True
    return False

class File(Rights): 
  def __init__(self):
    Rights.__init__(self)
    
class DirFileHelper:
  def concat_path(directory, name):
    return directory.path + '/' + name

class Directory(Rights):
  def __init__(self, path):
    Rights.__init__(self)
    self.path = path
    self.files = {}
    try:
      os.mkdir(path)
    except FileExistsError:
      pass
  def addFile(name, file_):
    self.files[name] = file_
    open(DirFileHelper.concat_path(self, name), 'w').close()
  def rmFile(name):
    os.unlink(DirFileHelper.concat_path(self, name))
    del self.files[name]
  def getFile(name):
    return self.files[name]
  def delete(self):
    os.rmdir(self.path)

Dir = Directory

class MetaInfo:
  def __init__(self):
    self.ocount = 0

def init(path):
  rpath = '/'
  for a in path.split('/'):
    try:
      os.mkdir(rpath)
    except FileExistsError:
      pass
    rpath = rpath + '/' + a

init(state_dir_path)
