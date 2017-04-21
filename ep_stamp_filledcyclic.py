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

import math
import model_random
import model_locus
import model_allele
import model_constraintpool
from gettext import gettext as _

ORDER_CONSTRAINT = 'orderconstaint'
RADIUS_CONSTRAINT = 'radiusconstraint'

class FilledCyclicStamp(model_allele.Allele):
    """FilledCyclicStamp:.
    inv: self.radius >= 0.0
    """

    cdef = [{'bind'  : ORDER_CONSTRAINT,
             'name'  : 'Natural logarithm of order p used in Minkowski distance',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 1.0, 'max': 4.0},
            {'bind'  : RADIUS_CONSTRAINT,
             'name'  : 'Radius of the filled cyclic polygon or circle',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.25},
           ]

    def __init__(self, trunk, dummy):
        """Constructor for a flip merger."""
        super(FilledCyclicStamp, self).__init__(trunk)
        self.order = 1.0 # special case for circle
        self.radius = 0.1

    def __eq__(self, other):
        """Equality based on radius."""
        equal = isinstance(other, FilledCyclicStamp) \
                and self.order == other.order \
                and self.radius == other.radius
        return equal

    def randomize(self):
        """Randomize the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.uniform_constrained(order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.uniform_constrained(radius_constraint)

    def mutate(self):
        """Make small random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.jitter_constrained(self.order, order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.jitter_constrained(self.radius, radius_constraint)

    def swap_places(self):
        """Nothing to do."""

    def crossingover(self, other):
        """
        pre: isinstance(other, FilledCyclicStamp)
        pre: isinstance(self, FilledCyclicStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = FilledCyclicStamp(self.get_trunk(), -1)
        cross_sequence = model_random.crossing_sequence(2)
        new_one.order = self.order if cross_sequence[0] else other.order
        new_one.radius = self.radius if cross_sequence[1] else other.radius
        return new_one

    def set_stamp_extent(self, width, height):
        """Set extent of stamp. This stamps will ignore these parameters."""
        pass

    def render(self, ctx, point, state):
        """
        pre: ctx is not None
        pre: len(point) == 2
        """
        edges = int(math.floor(self.order * self.order))
        if edges < 3:
            ctx.arc(point[0], point[1], self.radius, 0.0, 2.0*math.pi)
            ctx.fill()
        else:
            delta = 2.0*math.pi / edges
            start = -(delta / 2.0 + 0.5*math.pi)
            px = self.radius * math.cos(start)
            py = self.radius * math.sin(start)
            ctx.move_to(point[0] + px, point[1] + py)
            for step in range(1, edges):
                px = self.radius * math.cos(step * (delta) + start)
                py = self.radius * math.sin(step * (delta) + start)
                ctx.line_to(point[0] + px, point[1] + py)
            ctx.close_path()
            ctx.fill()

    def explain(self):
        """
        post: len(__return__) == 3
        """
        return _('Square root of number of edges: ') + str(self.order), \
               None, \
               None

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, FilledCyclicStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = FilledCyclicStamp(self.get_trunk(), -1)
        new_one.order = self.order
        new_one.radius = self.radius
        return new_one
