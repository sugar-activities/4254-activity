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

import types
import random

import ka_debug

class Locus(object):

    def _random_pattern(self):
        pattern = '_'
        for dummy in range(6):
            #                         12345678901234567890123456
            pattern += random.choice('abcdefghijklmnopqrstuvwxyz')
        pattern += '_'
        return pattern

    _modulo_count = 0

    def __init__(self, trunk):
        """
        pre: isinstance(trunk, str)
        pre: not (trunk == '')
        """
        self.create_unique_id()
        if trunk == '/':
            self.path = '/' + self.__class__.__name__
        else: 
            self.path = trunk + '/' + self.__class__.__name__ 
#        print '>>', self.path, self._unique_id

    def get_trunk(self):
        parts = self.path.split('/')
        if len(parts) > 2:
            trunk = ''
            for part in parts[1:-1]:
                if len(part) > 0:
                    trunk += '/' + part
            return trunk
        else:
            return '/'

    def create_unique_id(self):
        """ unique identification for this protozoon."""
        self._pattern = self._random_pattern()
        Locus._modulo_count = Locus._modulo_count + 1 \
                                   if Locus._modulo_count < 999999 else 0
        self._unique_id = self._pattern + str(Locus._modulo_count)

    def get_unique_id(self):
        """ unique identification for this protozoon."""
        return self._unique_id

    def dot(self):
        return ""

def unique_check(cpy, src1, src2):
    """Helper detecting violations against the 'deep copy' schema of 
    Locus subclasses. Only for use in design by contact statements."""
    error = ''
#    for k, v in cpy.__dict__.items():
#        print 'k, id(k), v:', isinstance(v, model_locus.Locus), type(v) == types.ListType, k, id(k), v
    for slot in cpy.__dict__:
        serr = None
        try:
            if isinstance(cpy.__dict__[slot], Locus):
#                print slot, id(cpy.__dict__[slot]), id(src1.__dict__[slot]), id(src2.__dict__[slot])
                if slot not in ['constraint']:
                    if(id(cpy.__dict__[slot]) == id(src1.__dict__[slot])):
                        serr = 'Copy error 1 ' + str(slot) + ': ' \
                                + str(cpy) + ', ' + str(src1)
                    if(id(cpy.__dict__[slot]) == id(src2.__dict__[slot])):
                        serr = 'Copy error 2 ' + str(slot) + ': ' \
                                + str(cpy) + ', ' + str(src2)
            if type(cpy.__dict__[slot]) == types.ListType:
#                print slot, cpy.__dict__[slot]
                for elem in cpy.__dict__[slot]:
                    if type(elem) not in [types.IntType, types.FloatType, types.StringType, types.UnicodeType]:
                        if ka_debug.contains_by_id(src1.__dict__[slot], elem):
                            serr = 'Copy error 3 ' + str(slot) + ' ' + str(elem) \
                                    + ': ' + str(cpy) + ', ' + str(src1)
                        if ka_debug.contains_by_id(src2.__dict__[slot], elem):
                            serr = 'Copy error 4 ' + str(slot) + ' ' + str(elem) \
                                    + ': ' + str(cpy) + ', ' + str(src2)
        except KeyError:
            error += 'KeyError ' + str(cpy.__dict__[slot]) + '\n' \
                                 + str(src2.__dict__[slot]) + '\n' \
                                 + str(src2.__dict__[slot]) + '\n'
        if serr is not None:
            error += serr
    if len(error) > 0:
        print error
    return error

