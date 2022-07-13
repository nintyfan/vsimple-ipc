
import threading
import inotify, inotify.adapters

class watcher(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.iadapter = inotify.adapters.Inotify()
    
  def run(self):
    for event in self.iadapter.event_gen(yield_nones=False):
      print(event)
  
  def add_path(self, path):
    self.iadapter.add_watch('/proc/' + path)
