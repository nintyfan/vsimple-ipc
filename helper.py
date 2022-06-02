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
import os

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
