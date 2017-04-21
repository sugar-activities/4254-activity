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
import ka_extensionpoint

import copy
import pickle
import zlib
import sys
import traceback
import os.path
import random

import ka_debug
import model_random
import model_protozoon
import model_history

STATE_INIT = 'I'
STATE_RANDOMIZED = 'R'
STATE_EVOLVED = 'E'

MAGIC_NUMBER = 'mk'
VERSION_NUMBER = '01'

class KandidModel(object):
    """
    inv: self.size >= 2
    inv: 1 <= self.fade_away <= self.size
    #inv: 0.0 <= self._flurry_rate <= 9.0
    inv: len(self.fitness) == self.size
    inv: forall(self.fitness, lambda f: 0.0 <= f <= 9.0)
    inv: len(self.protozoans) == self.size
    inv: forall(self.protozoans, lambda p:  p is not None)
    # all protozoans must be distinct objects, maybe with equal content
    inv: all_uniqe_reference(self.protozoans)
    """

    def __init__(self, init_size):
        self._state = STATE_INIT
        self.size = init_size
        self.fade_away = init_size / 2
        self.protozoans = [model_protozoon.Protozoon()
                                                 for dummy in range(self.size)]
        self.fitness = [3.0 for dummy in range(self.size)]
        ka_debug.info('initializing model with population size %u' % init_size)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.protozoans:
            result += ka_debug.dot_ref(anchor, ref)
        return result

    def copy(self):
        new_one = KandidModel(self.size)
        new_one.protozoans = [protoz.copy() for protoz in self.protozoans]
        new_one.fitness = [fit for fit in self.fitness]
        return new_one

    def set_flurry_rate(self, value):
        """Set amount of turbulence while breeding a new chromosome.
        pre: 0 <= value <= 9
        """
        model_random.set_flurry(value)

    def get_flurry_rate(self):
        """Returns amount of turbulence while breeding a new chromosome.
        post: 0 <= __return__ <= 9
        """
        return model_random.get_flurry()

    flurry_rate = property(get_flurry_rate, set_flurry_rate)

    def is_overwrite_allowed(self):
        """Preserve an already evolved population from over writing."""
        return not self._state == STATE_EVOLVED

    def classify(self):
        """Using fitness to build three distinct sets (good, moderate, poor). 
        # Return parameter 0: __return__[0] -> good
        # Return parameter 1: __return__[1] -> moderate
        # Return parameter 2: __return__[2] -> poor
        post: len(__return__[0])+len(__return__[1])+len(__return__[2]) == self.size
        post: len(__return__[0]) >= 1
        
        # mutual exclusive
        post: forall(__return__[0], lambda x: not contains_reference(x, __return__[1]))
        post: forall(__return__[0], lambda x: not contains_reference(x, __return__[2]))
        post: forall(__return__[2], lambda x: not contains_reference(x, __return__[0]))
        post: forall(__return__[2], lambda x: not contains_reference(x, __return__[1]))
        """
        good, moderate, poor = [], [], []
        # a new sorted list: 
        sorted_fitness = sorted(self.fitness)
        poor_level = sorted_fitness[self.fade_away-1]
        poor_level = 4 if poor_level > 4 else poor_level
        good_level = sorted_fitness[-1]
        for protoz, fit in zip(self.protozoans, self.fitness):
            if fit >= good_level and len(good) < 1:
                good.append(protoz)
            elif fit <= 0:
                poor.append(protoz)
            elif fit <= poor_level:
                if len(poor) >= self.fade_away:
                    index = random.randint(0, len(poor)-1)
                    moderate.append(poor[index])
                    del poor[index]
                poor.append(protoz)
            else:
                moderate.append(protoz)
        return good, moderate, poor

    def reduce_fitness(self, index):
        """Set fitness of a protozoon to the lowest value.
        pre: 0 <= index < len(self.fitness)
        post: self.fitness.count(0.0) >= 1
        """
        self.fitness[index] = 0.0
        
    def raise_fitness(self, index):
        """Set fitness of a protozoon to the highest value
        and reduce the fitness of all moderate protozoans by one. 
        pre: 0 <= index < len(self.fitness)
        post: self.fitness.count(9.0) == 1
        """
        for lower_at, fit in enumerate(self.fitness):
            if fit > 5.0:
                self.fitness[lower_at] = round(self.fitness[lower_at] - 1.0)
        self.fitness[index] = 9.0
        
    def randomize(self):
        self._state = STATE_RANDOMIZED
        for protoz in self.protozoans:
            protoz.randomize()

    def random(self):
        """Randomize protozoans with poor fitness.
        post: len(__return__) > 0
        post: forall(__return__, lambda x: 0 <= x < self.size)
        """
        new_indices = []
        self._state = STATE_EVOLVED
        dummy, dummy, poor = self.classify()
        for new_at, protoz in enumerate(self.protozoans):
            if protoz in poor:
                self.protozoans[new_at].create_unique_id()
                self.protozoans[new_at].randomize()
                self.fitness[new_at] = 3.0
                new_indices.append(new_at)
        return new_indices

    def breed_single(self, new_at):
        """Breed one new protozoon replacing the protozoon at index.
        post: len(__return__) > 0
        post: forall(__return__, lambda x: 0 <= x < self.size)
        """
        new_indices = [new_at]
        self._state = STATE_EVOLVED
        good, moderate, dummy = self.classify()
        self._breed(new_at, good, moderate)
        return new_indices

    def breed_generation(self):
        """Breed new protozoans replacing protozoans with poor fitness.
        post: len(__return__) > 0
        post: forall(__return__, lambda x: 0 <= x < self.size)
        """
        new_indices = []
        self._state = STATE_EVOLVED
        good, moderate, poor = self.classify()
        for new_at, protoz in enumerate(self.protozoans):
            if protoz in poor:
                self._breed(new_at, good, moderate)
                new_indices.append(new_at)
        return new_indices

    def _breed(self, new_at, good, moderate):
        partner = self.find_partner(moderate)
        new_one = good[0].crossingover(partner)
        new_one.swap_places()
        new_one.mutate()
        history = model_history.KandidHistory.instance()
        history.unlink(self.protozoans[new_at].get_unique_id())
#        ka_debug.info('new offspring ' + new_one.get_unique_id()
#                      + ' breeded by ' + good[0].get_unique_id() + ' and '
#                      + partner.get_unique_id() + ' replaced '
#                      + self.protozoans[new_at].get_unique_id())
        self.protozoans[new_at] = new_one
        self.fitness[new_at] = 4.0
        history.rember_parents(new_one.get_unique_id(),
                               good[0].get_unique_id(),
                               partner.get_unique_id())

    def find_partner(self, candidates):
        """Find a partner from the candidate list by chance.
        pre: len(candidates) > 0
        pre: forall(candidates, lambda candidate: candidate in self.protozoans)
        post: __return__ is not None
        post: __return__ in candidates
        """
        total = 0.0
        for index, protoz in enumerate(self.protozoans):
            if protoz in candidates:
                total += self.fitness[index]
        trigger = random.uniform(0.0, total)
        total = 0.0
        for index, protoz in enumerate(self.protozoans):
            if protoz in candidates:
                total += self.fitness[index]
                if trigger < total:
                    return protoz

    def replace(self, new_one):
        """Replace protozoon with lowest fitness.
        pre: isinstance(new_one, model_protozoon.Protozoon)
        """
        poor_level = 999999.9
        for protoz, fit in zip(self.protozoans, self.fitness):
            if fit < poor_level:
                poor_level = fit
                poor = protoz
        for new_at, protoz in enumerate(self.protozoans):
            if protoz is poor:
                #TODO history, forget former protozoans[new_at]
                self.protozoans[new_at] = new_one
                self.fitness[new_at] = 5.0
                return new_at
        return -1

def _get_my_revision():
    revision = ka_extensionpoint.revision_number
    return str(revision) if revision > 9  else '0' + str(revision)
        
def from_buffer(input_buffer):
#    ka_debug.info('read from_buffer')
    obj = None
    try:
        if input_buffer.startswith(MAGIC_NUMBER):
            obj = pickle.loads(zlib.decompress(input_buffer[4:]))
            if not input_buffer.startswith(MAGIC_NUMBER+_get_my_revision()):
                obj = obj.copy()
        else:
            ka_debug.err('missing magic number')
    except:
        ka_debug.err('failed reading input buffer [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)
    return obj

def to_buffer(obj):
#    ka_debug.info('write %s to_buffer' % type(obj))
    try:
        return MAGIC_NUMBER + _get_my_revision() \
               + zlib.compress(pickle.dumps(copy.deepcopy(obj), protocol=2))
    except:
        ka_debug.err('failed writing buffer [%s] [%s]' % \
                   (sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)
            
def read_file(file_path):
    model = None
    if os.path.isfile(file_path):
        in_file = None
        try:
            ka_debug.info('input file [%s]' % file_path)
            in_file = open(file_path, 'r')
            model = from_buffer(in_file.read())
            model._state = STATE_INIT
        except:
            ka_debug.err('failed reading [%s] [%s] [%s]' % \
                       (file_path, sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
        finally:
            if in_file:
                in_file.close()
    return model

def write_file(file_path, model):
    """Write model to the file system.
    pre: file_path is not None
    """
    out_file = None
    try:
        out_file = open(file_path, 'w')
        out_file.write(to_buffer(model))
    except:
        ka_debug.err('failed writing [%s] [%s] [%s]' % \
                   (file_path, sys.exc_info()[0], sys.exc_info()[1]))
        traceback.print_exc(file=sys.__stderr__)
    finally:
        if out_file:
            out_file.close()

def all_uniqe_reference(sequ):
    # Brute force is all that's left.
    unique = []
    for elem in sequ:
        if contains_reference(elem, unique):
            return False
        else:
            unique.append(elem)
    return len(unique) == len(sequ)
 
def contains_reference(find_elem, sequ):
    for elem in sequ:
        if id(find_elem) == id(elem):
            return True
    return False

