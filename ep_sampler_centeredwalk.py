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
import ka_utils

import model_locus
import model_random
import model_constraintpool
import ep_sampler_randomwalk
from gettext import gettext as _

SECTIONS_CONSTRAINT = 'sectionsconstraint'

class CenteredWalkSampler(ep_sampler_randomwalk.RandomWalkSampler):
    """CenteredWalkSampler: 
    inv: len(self.direction_steps) > 0
    """

    cdef = [{'bind'  : SECTIONS_CONSTRAINT,
             'name'  : 'Number of sections.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 100},
           ]

    def __init__(self, trunk):
        """Constructor for a random walk."""
        super(CenteredWalkSampler, self).__init__(trunk)

    def __eq__(self, other):
        """Equality."""
        equal = isinstance(other, CenteredWalkSampler) \
                and super(CenteredWalkSampler, self).__eq__(other)
        return equal

    def crossingover(self, other):
        """
        pre: isinstance(other, CenteredWalkSampler)
        pre: isinstance(self, CenteredWalkSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = CenteredWalkSampler(self.get_trunk())
        new_one.direction_steps = model_random.crossingover_list(self.direction_steps,
                                                              other.direction_steps)
        return new_one

    @staticmethod
    def _numeric_compare(point1, point2):
        """Comparison function based on Euklidian distance from center 0.0."""
        diff1 = point1[0]*point1[0] + point1[1]*point1[1]
        diff2 = point2[0]*point2[0] + point2[1]*point2[1]
        if diff1 > diff2:
            return 1
        elif diff1 < diff2:
            return -1
        return 0

    def get_sample_points(self):
        """ Produces a list of sampling points.
        The points describes an random walk starting near (0.5, 0.5).
        """
        sample_points = super(CenteredWalkSampler, self).get_sample_points()
        sample_points.sort(cmp=CenteredWalkSampler._numeric_compare,
                           reverse=False)
        return sample_points

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Centered random walk sampler: %d points') \
                                            % (len(self.direction_steps))
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, CenteredWalkSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = CenteredWalkSampler(self.get_trunk())
        new_one.direction_steps = model_random.copy_list(self.direction_steps)
        return new_one
