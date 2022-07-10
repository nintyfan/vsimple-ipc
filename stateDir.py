
class File:
  def __init__(self):
    self.unixRights = 0o777
  def setRights(rights):
    self.unixRights = rights
  def getRights():
    return self.unixRights
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

class DirFileHelper:
  def concat_path(directory, name):
    return directory.path + '/' + name

class Directory:
  def __init__(self, path):
    self.path = path
    self.files = {}
    os.mkdir(path)
  def addFile(name, file_):
    self.files[name] = file_
    open(DirFileHelper.concat_path(self, name), 'w').close()
  def rmFile(name):
    os.unlink(DirFileHelper.concat_path(self, name))
    del self.files[name]
  def getFile(name):
    return self.files[name]

