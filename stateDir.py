
class File:
  def __init__(self):
    self.unixRights = 0o777
  def setRights(rights):
    self.unixRights = rights
  def getRights():
    return self.unixRights

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

