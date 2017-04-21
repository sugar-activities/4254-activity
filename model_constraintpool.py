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

#_CONSTRAINT = 'constraint'

INT_1_OF_N    = 11
INT_M_OF_N    = 12
INT_RANGE     = 13
FLOAT_RANGE   = 22
STRING_1_OF_N = 31
STRING_M_OF_N = 32

class ConstraintPool(object):
    """ConstraintPool is a singleton.
    Use ConstraintPool.get_pool() to get an instance.
    """

    _constraintpool = None
    _known_keys = None

    def __init__(self):
        self._overwrite = {}
        self._my_defaults()
        self._depricated = ['border', ]

    @staticmethod
    def get_pool():
        if ConstraintPool._constraintpool == None:
            ConstraintPool._constraintpool = ConstraintPool()
        return ConstraintPool._constraintpool

    def _generate_key(self, class_key, attribute_key):
        """
        pre: class_key is not None
        pre: attribute_key is not None
        """
        return class_key + '/' + attribute_key

    def get(self, caller, attribute_key):
        """
        #pre: 'cdef' in dir(caller) or 'base_cdef' in dir(caller) 
        pre: True if 'cdef' not in dir(caller) else caller.cdef is not None and len(caller.cdef) > 0
        pre: True if 'base_cdef' not in dir(caller) else caller.base_cdef is not None and len(caller.base_cdef) > 0
        pre: caller.path is not None
        pre: attribute_key is not None
        post: __return__ is not None
        """
        primary_key = self._generate_key(caller.path, attribute_key)
        secondary_key = self._generate_key('*', attribute_key)
        result = None
        if self._overwrite.has_key(primary_key):
            result = self._overwrite[primary_key]
#            print '>> over', primary_key, result
        elif self._overwrite.has_key(secondary_key):
            result = self._overwrite[secondary_key]
#            print '>> over', primary_key, result
        else:
            if 'cdef' in dir(caller):
                result = self._search_constraint(caller.cdef, attribute_key)
            if result is None and 'base_cdef' in dir(caller):
                result = self._search_constraint(caller.base_cdef, attribute_key)
#        print '>> cdef', primary_key, result
        if result is not None:
            result = [x for x in result if x not in self._depricated]
            self._add_key(primary_key)
        return result

    def _search_constraint(self, caller, attribute_key):
        result = None
        for definition in caller:
            if definition['bind'] == attribute_key:
                if definition['domain'] == INT_1_OF_N:
                    result = [x[1] for x in definition['enum']]
                if definition['domain'] == INT_M_OF_N:
                    result = [x[1] for x in definition['enum']]
                if definition['domain'] == INT_RANGE:
                    result = (definition['min'], definition['max'])
                if definition['domain'] == FLOAT_RANGE:
                    result = (definition['min'], definition['max'])
                if definition['domain'] == STRING_1_OF_N:
                    result = definition['enum']
                if definition['domain'] == STRING_M_OF_N:
                    result = definition['enum']
        return result

    def is_overwritten(self, caller, attribute_key):
        return False

    def set(self, class_key, attribute_key, constraint):
        """
        pre: class_key is not None
        pre: class_key.startswith('/') or class_key.startswith('*')
        pre: attribute_key is not None
        pre: constraint is not None
        """
        primary_key = self._generate_key(class_key, attribute_key)
        self._overwrite[primary_key] = constraint

    def clear_all(self):
        """
        """
        self._overwrite = {}

    def listknown_keys(self):
        """
        """
        return [] if ConstraintPool._known_keys is None \
                  else ConstraintPool._known_keys

    def _add_key(self, key):
        """
        """
#        file_path = '/dev/shm/minmal_known_keys.mkey'
#        if ConstraintPool._known_keys is None:
#            ConstraintPool._known_keys = model_population.read_file(file_path)
        if ConstraintPool._known_keys is None:
            ConstraintPool._known_keys = []
        if key not in ConstraintPool._known_keys:
            ConstraintPool._known_keys.append(key)
#            model_population.write_file(file_path, ConstraintPool._known_keys)

    def _my_defaults(self):
        #TODO read from persistence, provide an constraint editor
#        self.set('*', 'layertypeconstraint', ['filledspline', ])
#        self.set('*', 'layertypeconstraint', ['voronoidiagram', 'markovchain', 'lca', 'letterpress', 'quadtree', ])
#        self.set('*', 'layertypeconstraint', ['lca', ])
#        self.set('*', 'layertypeconstraint', ['image', ])
#        self.set('*', 'layertypeconstraint', ['markovchain', ])
#        self.set('*', 'layertypeconstraint', ['referencepattern', ])
#        self.set('*', 'layertypeconstraint', ['quadtree', ])
#        self.set('*', 'layertypeconstraint', ['voronoidiagram', 'markovchain', ])

#        self.set('*', 'mergertypeconstraint', ['combine',])
#        self.set('*', 'mergertypeconstraint', ['mask', ])

#        self.set('*', 'modifiertypeconstraint', ['flip', ])
#        self.set('*', 'modifiertypeconstraint', ['border', ])
#        self.set('*', 'modifiertypeconstraint', ['rectangulartile', ])

#        self.set('*', 'stamptypeconstraint', ['star',])
#        self.set('*', 'stamptypeconstraint', ['disk',])
#        self.set('*', 'stamptypeconstraint', ['filledcyclic',])
#        self.set('*', 'stamptypeconstraint', ['svg',])
#        self.set('*', 'stamptypeconstraint', ['glyph',])

#        self.set('*', 'samplertypeconstraint', ['logarithmicspiral', ])
#        self.set('*', 'samplertypeconstraint', ['fermatspiral', ])
#        self.set('*', 'samplertypeconstraint', ['squaregrid',])
#        self.set('*', 'samplertypeconstraint', ['affineifs',])
#        self.set('*', 'samplertypeconstraint', ['randomwalk',])

#        self.set('*', 'colorconstraint', ['colorconstraint_none', ])

#        self.set('*', 'glyphcategoryconstraint', ['Sc','Po',])

#        self.set('*', 'themeconstraint', ['cybernetic_serendipity',])

#        self.set('*', 'number_of_statesconstraint', (5, 5))

#        self.set('*', 'tilesconstraint', (3, 3))
        pass
