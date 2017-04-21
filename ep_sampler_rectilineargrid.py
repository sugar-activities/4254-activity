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

X_TILES_CONSTRAINT = 'xtilesconstraint'
Y_TILES_CONSTRAINT = 'ytilesconstraint'

class RectilinearGridSampler(model_allele.Allele):
    """RectilinearGridSampler: Reverse the layer horizontally or vertically.
    inv: self.x_tiles > 0
    inv: self.y_tiles > 0
    """

    cdef = [{'bind'  : X_TILES_CONSTRAINT,
             'name'  : 'Number of rectilinear tiles in x direction',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 24},
             {'bind'  : Y_TILES_CONSTRAINT,
             'name'  : 'Number of rectilinear tiles in y direction',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 24},
           ]

    def __init__(self, trunk):
        """Constructor for a flip merger."""
        super(RectilinearGridSampler, self).__init__(trunk)
        self.x_tiles = 1
        self.y_tiles = 1

    def __eq__(self, other):
        """Equality based on fliping horizontally or vertically."""
        equal = isinstance(other, RectilinearGridSampler) \
                and self.x_tiles == other.x_tiles \
                and self.y_tiles == other.y_tiles
        return equal

    def randomize(self):
        """Randomizes the number of tiles."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        x_tiles_constraint = cpool.get(self, X_TILES_CONSTRAINT)
        self.x_tiles = model_random.randint_constrained(x_tiles_constraint)
        y_tiles_constraint = cpool.get(self, Y_TILES_CONSTRAINT)
        self.y_tiles = model_random.randint_constrained(y_tiles_constraint)

    def mutate(self):
        """Mutates the number of tiles."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        if model_random.is_mutating():
            x_tiles_constraint = cpool.get(self, X_TILES_CONSTRAINT)
            self.x_tiles = model_random.jitter_discret_constrained(self.x_tiles,
                                                            x_tiles_constraint)
        if model_random.is_mutating():
            y_tiles_constraint = cpool.get(self, Y_TILES_CONSTRAINT)
            self.y_tiles = model_random.jitter_discret_constrained(self.y_tiles,
                                                            y_tiles_constraint)

    def swap_places(self):
        """Exchange x- and y-tiles."""
        self.x_tiles, self.y_tiles = model_random.swap_parameters(self.x_tiles,
                                                             self.y_tiles)

    def crossingover(self, other):
        """
        pre: isinstance(other, RectilinearGridSampler)
        pre: isinstance(self, RectilinearGridSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = RectilinearGridSampler(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(2)
        new_one.x_tiles = self.x_tiles if cross_sequence[0] else other.x_tiles
        new_one.y_tiles = self.y_tiles if cross_sequence[1] else other.y_tiles
        return new_one

    def get_sample_points(self):
        """ Produces a list of sampling points.
        """
        sample_points = []
        dx, dy  = 1.0 / self.x_tiles, 1.0 / self.y_tiles
        for tx in range(self.x_tiles):
            xp = dx*(tx+0.5)
            for ty in range(self.y_tiles):
                sample_points.append( (xp-0.5, dy*(ty+0.5)-0.5) )
        return sample_points

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        return 1.0/self.x_tiles, 1.0/self.y_tiles

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Rectilinear grid sampler: %d*x, %d*y') \
                                            % (self.x_tiles, self.y_tiles)
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, RectilinearGridSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = RectilinearGridSampler(self.get_trunk())
        new_one.x_tiles = self.x_tiles
        new_one.y_tiles = self.y_tiles
        return new_one
