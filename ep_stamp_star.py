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

import model_random
import model_locus
import model_allele
import model_constraintpool
import random
import cairo

ORDER_CONSTRAINT = 'orderconstaint'
RADIUS_CONSTRAINT = 'radiusconstraint'
SCATTER_CONSTRAINT = 'scatterconstraint'
LINE_WIDTH_CONSTRAINT = 'linewidthconstraint'
START_ANGLE_CONSTRAINT = 'startangleconstraint'

class StarStamp(model_allele.Allele):
    """StarStamp:.
    inv: self.radius >= 0.0
    inv: self.scatter >= 0.0
    """

    cdef = [{'bind'  : ORDER_CONSTRAINT,
             'name'  : 'Number of rays',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 3, 'max': 17},
            {'bind'  : RADIUS_CONSTRAINT,
             'name'  : 'Radius of the star',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.33},
            {'bind'  : SCATTER_CONSTRAINT,
             'name'  : 'Scattering the rays length',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.99},
            {'bind'  : START_ANGLE_CONSTRAINT,
             'name'  : 'Rotation of the stamp',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -math.pi, 'max': math.pi},
            {'bind'  : LINE_WIDTH_CONSTRAINT,
             'name'  : 'Line width of the rays',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.001, 'max': 0.025},
           ]

    def __init__(self, trunk, dummy):
        """Constructor for a star stamp."""
        super(StarStamp, self).__init__(trunk)
        self.order = 1
        self.radius = 0.1
        self.scatter = 0.1
        self.start_angle = 0.0
        self.line_width = 0.025
        self.random_seed = 1512

    def __eq__(self, other):
        """Equality based on radius."""
        equal = isinstance(other, StarStamp) \
                and self.order == other.order \
                and self.radius == other.radius \
                and self.scatter == other.scatter \
                and self.start_angle == other.start_angle \
                and self.line_width == other.line_width \
                and self.random_seed == other.random_seed
        return equal

    def randomize(self):
        """Randomize the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.randint_constrained(order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.uniform_constrained(radius_constraint)
        scatter_constraint = cpool.get(self, SCATTER_CONSTRAINT)
        self.scatter = model_random.uniform_constrained(scatter_constraint)
        start_angle_constraint = cpool.get(self, START_ANGLE_CONSTRAINT)
        self.start_angle = model_random.uniform_constrained(start_angle_constraint)
        line_width_constraint = cpool.get(self, LINE_WIDTH_CONSTRAINT)
        self.line_width = model_random.uniform_constrained(line_width_constraint)
        self.random_seed = random.randint(1, 65535)

    def mutate(self):
        """Make small random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.jitter_discret_constrained(self.order, order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.jitter_constrained(self.radius, radius_constraint)
        scatter_constraint = cpool.get(self, SCATTER_CONSTRAINT)
        self.scatter = model_random.jitter_constrained(self.scatter, scatter_constraint)
        start_angle_constraint = cpool.get(self, START_ANGLE_CONSTRAINT)
        self.start_angle = model_random.jitter_constrained(self.start_angle, start_angle_constraint)
        line_width_constraint = cpool.get(self, LINE_WIDTH_CONSTRAINT)
        self.line_width = model_random.jitter_constrained(self.line_width, line_width_constraint)

    def swap_places(self):
        """Nothing to do."""

    def crossingover(self, other):
        """
        pre: isinstance(other, StarStamp)
        pre: isinstance(self, StarStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = StarStamp(self.get_trunk(), -1)
        cross_sequence = model_random.crossing_sequence(6)
        new_one.order = self.order if cross_sequence[0] else other.order
        new_one.radius = self.radius if cross_sequence[1] else other.radius
        new_one.scatter = self.scatter if cross_sequence[2] else other.scatter
        new_one.start_angle = self.start_angle if cross_sequence[3] else other.start_angle
        new_one.line_width = self.line_width if cross_sequence[4] else other.line_width
        new_one.random_seed = self.random_seed \
                         if cross_sequence[5] else other.random_seed
        return new_one

    def set_stamp_extent(self, width, height):
        """Set extent of stamp. This stamps will ignore these parameters."""
        pass

    def render(self, ctx, point, state):
        """
        pre: ctx is not None
        pre: len(point) == 2
        """
        ctx.set_line_width(self.line_width)
        factor = 2.0 * math.pi / float(self.order)
        rale = random.Random()
#        rale.seed(self.order+100*self.line_width+100*self.start_angle)
        rale.seed(state+self.random_seed)
        line_cap = ctx.get_line_cap()
        if self.line_width > 0.005:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        min_jitter, max_jitter = 1.0-self.scatter, 1.0+self.scatter
        centre_x, centre_y = point[0], point[1]
        for step in xrange(self.order + 1):
            angle = factor * step + self.start_angle
            jittered_radius = self.radius * rale.uniform(min_jitter, max_jitter)
            ctx.move_to(centre_x, centre_y)
            ctx.line_to(centre_x + jittered_radius * math.cos(angle),
                        centre_y + jittered_radius * math.sin(angle))
        ctx.stroke()
        ctx.set_line_cap(line_cap)

    def explain(self):
        """
        post: len(__return__) == 3
        """
        str_start_angle = _('start angle: %4.3f') % self.start_angle
        str_line_width = _('line width: %4.3f') % self.line_width
        return _('Star stamp: number of rays: ') + str(self.order) \
               + ', ' + str_line_width \
               + ', ' + str_start_angle , \
               None, \
               None

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, StarStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = StarStamp(self.get_trunk(), -1)
        new_one.order = self.order
        new_one.radius = self.radius
        new_one.scatter = self.scatter
        new_one.line_width = self.line_width
        new_one.start_angle = self.start_angle
        new_one.random_seed = self.random_seed
        return new_one
