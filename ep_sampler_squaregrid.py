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
import model_random
import model_locus
import model_allele
import model_constraintpool
from gettext import gettext as _

TILES_CONSTRAINT = 'tilesconstraint'

class SquareGridSampler(model_allele.Allele):
    """SquareGridSampler: Reverse the layer horizontally or vertically.
    inv: self.tiles > 0
    """

    cdef = [{'bind'  : TILES_CONSTRAINT,
             'name'  : 'Number of rectilinear tiles.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 24},
           ]

    def __init__(self, trunk):
        """Constructor for a flip merger."""
        super(SquareGridSampler, self).__init__(trunk)
        self.tiles = 1

    def __eq__(self, other):
        """Equality based on on number of tiles."""
        equal = isinstance(other, SquareGridSampler) \
                and self.tiles == other.tiles
        return equal

    def randomize(self):
        """Randomizes the number of tiles."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        tiles_constraint = cpool.get(self, TILES_CONSTRAINT)
        self.tiles = model_random.randint_constrained(tiles_constraint)

    def mutate(self):
        """Mutates the number of tiles."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        if model_random.is_mutating():
            tiles_constraint = cpool.get(self, TILES_CONSTRAINT)
            self.tiles = model_random.jitter_discret_constrained(self.tiles,
                                                            tiles_constraint)

    def swap_places(self):
        """Do nothing."""

    def crossingover(self, other):
        """
        pre: isinstance(other, SquareGridSampler)
        pre: isinstance(self, SquareGridSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = SquareGridSampler(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(1)
        new_one.tiles = self.tiles if cross_sequence[0] else other.tiles
        return new_one

    def get_sample_points(self):
        """Produces a list of sampling points.
        """
        sample_points = []
        delta  = 1.0 / self.tiles
        for tx in range(self.tiles):
            xp = delta*(tx+0.5)
            for ty in range(self.tiles):
                sample_points.append( (xp-0.5, delta*(ty+0.5)-0.5) )
        return sample_points

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        return 1.0/self.tiles, 1.0/self.tiles

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Squarish grid sampler: %d*%d') \
                                            % (self.tiles, self.tiles)
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, SquareGridSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = SquareGridSampler(self.get_trunk())
        new_one.tiles = self.tiles
        return new_one
