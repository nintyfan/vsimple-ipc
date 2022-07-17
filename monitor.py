
import threading
import inotify, inotify.adapters

import stateDir
from main import Helper  as sHelper

class watcher(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.iadapter = inotify.adapters.Inotify()
    
  def run(self):
    for event in self.iadapter.event_gen(yield_nones=False):
      print(event)
      (_, event_type, path, filename) = event
      
      if path != '/proc':
        continue
      
      try:
        int(filename)
      except ValueError:
        continue
      
      if 'IN_CREATE' in event_type:
        pass
      
      if 'IN_DELETE' in event_type:
        mHelper.release_stateDir_if_needed(filename)

        
  def add_path(self, path):
    # self.iadapter.add_watch('/vsimple-ipc/' + path)
    self.iadapter.add_watch('/proc/' + path)
