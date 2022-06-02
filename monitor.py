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
import threading
import inotify, inotify.adapters

class watcher(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.iadapter = None
    
  def run(self):
    self.iadapter = inotify.adapters.Inotify()
    self.iadapter.add_watch('/proc')
    for event in self.iadapter.event_gen(yield_nones=False):
      print(event)
