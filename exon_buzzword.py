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

import random

import ka_debug
import model_random
import ka_extensionpoint
import model_constraintpool
import model_locus
import model_allele

BUZZWORD_CONSTRAINTS = 'buzzwordconstraint'

class Buzzword(model_allele.Allele):
    """Buzzword
    inv: len(self.wordlist) > 0
    """

    cdef = [{'bind'  : BUZZWORD_CONSTRAINTS,
             'name'  : 'Buzzwords',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_extensionpoint.list_extensions(BUZZWORD_CONSTRAINTS)
            },
           ]

    def __init__(self, trunk, words):
        """Buzzword constructor
        pre: len(words) > 0
        """
        super(Buzzword, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraint_name = cpool.get(self, BUZZWORD_CONSTRAINTS)[0]
        self.constraint = ka_extensionpoint.create(constraint_name, self.path)
        self.wordlist = words

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.wordlist:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality based on list of strings."""
        equal = isinstance(other, Buzzword) \
                and len(self.wordlist) == len(other.wordlist)
        if equal:
            for index, word in enumerate(self.wordlist):
                equal = equal and word == other.wordlist[index]
        return equal

#    def __ne__(self, other):
#        return not self.__eq__(other)
#
#    def __hash__(self):
#        raise TypeError("Genome objects are unhashable")

    def randomize(self):
        """Create a random word list.
        Result is a subset of the word list from
        extension point 'ep_buzzwordconstraint'.
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraints = cpool.get(self, BUZZWORD_CONSTRAINTS)
        self.constraint = ka_extensionpoint.create(random.choice(constraints),
                                                                     self.path)

        full_wordlist = self.constraint.get_wordlist()
        approximate_count = random.randint(1, len(full_wordlist)-1)
        self.wordlist = []
        self.wordlist.append(random.choice(full_wordlist))
        for dummy in range(approximate_count):
            candidate = random.choice(full_wordlist)
            if candidate not in self.wordlist:
                self.wordlist.append(candidate)

    def mutate(self):
        """Mutate word list.
        """
        full_wordlist = self.constraint.get_wordlist()

        # change a word
        if model_random.is_mutating():
            candidate = random.choice(full_wordlist)
            if candidate not in self.wordlist:
                self.wordlist[random.randint(0, len(self.wordlist)-1)] = \
                                                                     candidate

        # change number of words
        if model_random.is_mutating():
            new_count = len(self.wordlist) + random.randint(-1, 1)
            if new_count > len(self.wordlist):
                # append one
                self.wordlist.insert(random.randint(0, len(self.wordlist)-1), \
                                     random.choice(full_wordlist))
            elif new_count < len(self.wordlist) and len(self.wordlist) >= 2:
                #remove one
                del self.wordlist[random.randint(0, len(self.wordlist)-1)]

    def swap_places(self):
        """Exchange position of buzzwords in word list"""
        model_random.swap_places(self.wordlist)

    def crossingover(self, other):
        """Merges both word lists and returns a copy of Buzzword.
        pre: isinstance(other, Buzzword)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = Buzzword(self.get_trunk(), [''])
        new_one.wordlist = model_random.crossingover_str_list(self.wordlist,
                                                              other.wordlist)
        return new_one

    def copy(self):
        """A word list copy constructor.
        post: isinstance(__return__, Buzzword)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = Buzzword(self.get_trunk(), [''])
        new_one.wordlist = []
        for word in self.wordlist:
            new_one.wordlist.append(word[:])
        new_one.constraint = self.constraint
        return new_one
