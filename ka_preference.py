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

import ka_debug
import ka_importer
import os
import sys
import traceback

EXPORT_SIZE       = 'export_size'

class Preference(object):
    """
    inv: self._preference_dict is not None
    """
    _preference = None

    def __init__(self):
        """
        """
        self._dirty_flag = False
        self._first_get = False
        self._preference_dict = {}

    @staticmethod
    def instance():
        if Preference._preference is None:
            Preference._preference = Preference()
        return Preference._preference
    
    def set(self, topic, value):
        """
        pre: topic is not None
        pre: value is not None
        """
        self._dirty_flag = True
        self._preference_dict[topic] = value

    def get(self, topic):
        """
        pre: topic is not None
        """
        if not self._first_get:
            self._default()
            self.recall();
            self._first_get = True
        return self._preference_dict[topic] if topic in self._preference_dict \
                                            else None

    def isDirty(self):
        return self._dirty_flag

    def _file_name(self):
        target_path = ka_importer.get_data_path()
        return os.path.join(target_path, 'user_prefereces')

    def _default(self):
        self._preference_dict = {EXPORT_SIZE: (400, 400)}

    def store(self):
        """Write textual content to the file system.
        """
        if self._dirty_flag:
            out_file = None
            fn = ''
            try:
                fn = self._file_name()
                out_file = open(fn, 'w')
                out_file.write(repr(self._preference_dict))
                self._dirty_flag = False
            except:
                ka_debug.err('failed writing [%s] [%s] [%s]' % \
                           (fn, sys.exc_info()[0], sys.exc_info()[1]))
                traceback.print_exc(file=sys.__stderr__)
            finally:
                if out_file:
                    out_file.close()

    def recall(self):
        """
        """
        in_file = None
        fn = ''
        try:
            fn = self._file_name()
            if os.path.exists(fn):
                in_file = open(fn, 'r')
                self._preference_dict = eval(in_file.read())
        except:
            ka_debug.err('failed reading [%s] [%s] [%s]' % \
                       (fn, sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        finally:
            if in_file:
                in_file.close()
