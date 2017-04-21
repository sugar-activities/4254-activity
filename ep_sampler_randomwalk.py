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

import math

import ka_debug
import ka_utils
import model_random
import model_locus
import model_allele
import model_constraintpool
import exon_direction

SECTIONS_CONSTRAINT = 'sectionsconstraint'

class RandomWalkSampler(model_allele.Allele):
    """RandomWalkSampler: 
    inv: len(self.direction_steps) > 0
    """

    cdef = [{'bind'  : SECTIONS_CONSTRAINT,
             'name'  : 'Number of sections.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 100},
           ]

    def __init__(self, trunk):
        """Constructor for a random walk."""
        super(RandomWalkSampler, self).__init__(trunk)
        self.direction_steps = [exon_direction.Direction(self.path, 0.0, 0.0)]

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.direction_steps:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality."""
        equal = isinstance(other, RandomWalkSampler) \
                and len(self.direction_steps) == len(other.direction_steps)
        if equal:
            for index, direction in enumerate(self.direction_steps):
                equal = equal and direction == other.direction_steps[index]
        return equal

    def randomize(self):
        """Randomizes the walk."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        sections_constraint = cpool.get(self, SECTIONS_CONSTRAINT)
        for dummy in range(model_random.randint_constrained(sections_constraint)):
            direction = exon_direction.Direction(self.path, 0.0, 0.0)
            direction.randomize()
            self.direction_steps.append(direction)

    def mutate(self):
        """Mutates the random walk."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        sections_constraint = cpool.get(self, SECTIONS_CONSTRAINT)
        if model_random.is_mutating():
            model_random.mutate_list(self.direction_steps, sections_constraint,
                                exon_direction.Direction(self.path, 0.0, 0.0))

    def swap_places(self):
        """Reorder steps."""
        model_random.swap_places(self.direction_steps)

    def crossingover(self, other):
        """
        pre: isinstance(other, RandomWalkSampler)
        pre: isinstance(self, RandomWalkSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = RandomWalkSampler(self.get_trunk())
        new_one.direction_steps = model_random.crossingover_list(self.direction_steps,
                                                              other.direction_steps)
        return new_one

    def get_sample_points(self):
        """ Produces a list of sampling points.
        The points describes an random walk starting near (0.0, 0.0).
        """
        sample_points = []
        px, py = 0.0, 0.0
        for step in self.direction_steps:
            px += step.offset * math.cos(step.radian)
            py += step.offset * math.sin(step.radian)
            sample_points.append( (px, py) )
        return sample_points

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        aproximately = 1.0 / math.sqrt(1.0*len(self.direction_steps))
        return aproximately, aproximately

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Random walk sampler: %d points') \
                                            % (len(self.direction_steps))
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, RandomWalkSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = RandomWalkSampler(self.get_trunk())
        new_one.direction_steps = model_random.copy_list(self.direction_steps)
        return new_one
