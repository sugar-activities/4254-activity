# coding: UTF-8
# Copyright 2009, 2010 Thomas Jourdan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gettext import gettext as _
import os
import sys
import traceback

import ka_debug
import ka_extensionpoint

_proc_status = '/proc/%d/status' % os.getpid()

TOPIC_COLLABORATION       = 1000
SUB_ID                    =    1
SUB_SHARE                 =    2
SUB_TUBES                 =    3
SUB_BUDDIES_PARTICIPATING =    4
SUB_BUDDIES_JOINED        =    5
SUB_BUDDIES_LEFT          =    6
SUB_RECEIVED              =    7
SUB_BUDDIES_FOUND         =    8

TOPIC_TASK                = 2000
SUB_UNFINISHED            =    1
SUB_THREADS               =    2
SUB_VM_SIZE               =    3
SUB_VM_PEAK               =    4
SUB_VM_RSS                =    5
SUB_PID                =    6

TOPIC_ACTIVTY             = 9000
SUB_REVISION              =    1

TOPIC = {TOPIC_COLLABORATION: _('Collaboration'),
         TOPIC_COLLABORATION+SUB_ID: _('My ID'),
         TOPIC_COLLABORATION+SUB_SHARE: _('Share'),
         TOPIC_COLLABORATION+SUB_TUBES: _('My tubes'),
         TOPIC_COLLABORATION+SUB_BUDDIES_PARTICIPATING: _('Buddies participating'),
         TOPIC_COLLABORATION+SUB_BUDDIES_JOINED: _('Buddies joined'),
         TOPIC_COLLABORATION+SUB_BUDDIES_LEFT: _('Buddies left'),
         TOPIC_COLLABORATION+SUB_RECEIVED: _('Received latest'),
         TOPIC_COLLABORATION+SUB_BUDDIES_FOUND: _('Buddies found during startup'),

         TOPIC_TASK: _('Tasks'),
         TOPIC_TASK+SUB_UNFINISHED: _('Unfinished tasks'),
         TOPIC_TASK+SUB_THREADS: _('Threads'),
         TOPIC_TASK+SUB_VM_SIZE: _('Virtual memory size'),
         TOPIC_TASK+SUB_VM_PEAK: _('Virtual memory peak size'),
         TOPIC_TASK+SUB_VM_RSS: _('Resident set size'),
         TOPIC_TASK+SUB_PID: _('Process ID'),

         TOPIC_ACTIVTY: _('Activity'),
         TOPIC_ACTIVTY+SUB_REVISION: _('Running'),
        }

class Status(object):
    """
    inv: self._status_dict is not None
    """

    _status = None

    def __init__(self):
        """
        """
        self._dirty_flag = True
        self._status_dict = {}
        value = 'Kandid, release v' + str(ka_extensionpoint.revision_number)
        value = value + ', DoB activated' if ka_debug.is_DbC_activated \
                                          else value
        self.set(TOPIC_ACTIVTY, SUB_REVISION, value)
        self.set(TOPIC_TASK, SUB_PID, str(os.getpid()))

    @staticmethod
    def instance():
        if Status._status is None:
            Status._status = Status()
        return Status._status
    
    def set(self, topic, sub, value):
        """
        pre: topic >= 1000 and topic <= TOPIC_ACTIVTY and topic % 1000 == 0
        pre: sub > 0 and sub < 1000
        pre: value is not None
        """
        self._dirty_flag = True
        if str(type(value)) == "<type 'set'>":
            self._status_dict[topic+sub] = str(value)[5:-2]
        elif str(type(value)) == "<type 'list'>":
            self._status_dict[topic+sub] = str(value)[1:-1]
        else:
            self._status_dict[topic+sub] = value

    def isDirty(self):
        return self._dirty_flag

    def recall(self):
        """
        post: __return__ is not None
        """
        self._dirty_flag = False
        keys = self._status_dict.keys()
        keys.sort()
        text = ''
        topic_head = 0
        for key in keys:
            if not key / 1000 == topic_head:
                text += '\n' + TOPIC[key - key % 1000] + '\n'
                topic_head = key / 1000
            text += '  ' + TOPIC[key] + ': ' + self._status_dict[key] + '\n'
        return text


    def _set_process_status(self, os_status, key, sub):
        pos = os_status.index(key)
        num_tokens = 3 if key.startswith('Vm') else 2
        tri = os_status[pos:].split(None, num_tokens) # whitespace
        pos, pretty = 0, ''
        for digit in tri[1][::-1]:
            if pos > 0 and pos % 3 == 0:
                pretty = '.' + pretty
            pretty = digit + pretty
            pos += 1
        if num_tokens > 2:
            self.set(TOPIC_TASK, sub, pretty + ' ' + tri[2])
        else:
            self.set(TOPIC_TASK, sub, pretty)
        return pos

    def scan_os_status(self):
        """see
        http://linuxdevcenter.com/pub/a/linux/2006/11/30/linux-out-of-memory.html
        """
        try:
            proc = open(_proc_status)
            os_status = proc.read()
            self._set_process_status(os_status, 'Threads:', SUB_THREADS)
            self._set_process_status(os_status, 'VmSize:', SUB_VM_SIZE)
            self._set_process_status(os_status, 'VmPeak:', SUB_VM_PEAK)
            self._set_process_status(os_status, 'VmRSS:', SUB_VM_RSS)
            proc.close()
        except:
            # non Linux?
            ka_debug.err('scan_os_status [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
