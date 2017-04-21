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
import cairo

ORDER_CONSTRAINT = 'orderconstaint'
RADIUS_CONSTRAINT = 'radiusconstraint'
SCALE_CONSTRAINT = 'scaleconstraint'
DIM_OUT_CONSTRAINT = 'dimoutconstraint'

class DiskStamp(model_allele.Allele):
    """DiskStamp:.
    inv: self.radius >= 0.0
    """

    cdef = [{'bind'  : ORDER_CONSTRAINT,
             'name'  : 'Number of nested disks',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 1.0, 'max': 8.0},
            {'bind'  : RADIUS_CONSTRAINT,
             'name'  : 'Radius of the filled cyclic polygon or circle',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.25},
            {'bind'  : DIM_OUT_CONSTRAINT,
             'name'  : 'Difference in luminosity between successive disks',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.1, 'max': 1.25},
            {'bind'  : SCALE_CONSTRAINT,
             'name'  : 'Difference in the radius between successive disks',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.025, 'max': 0.975},
           ]

    def __init__(self, trunk, dummy):
        """Constructor for a flip merger."""
        super(DiskStamp, self).__init__(trunk)
        self.order = 1.0
        self.radius = 0.1
        self.scale = 0.5
        self.dim_out = 0.5

    def __eq__(self, other):
        """Equality based on radius."""
        equal = isinstance(other, DiskStamp) \
                and self.order == other.order \
                and self.radius == other.radius \
                and self.scale == other.scale \
                and self.dim_out == other.dim_out
        return equal

    def randomize(self):
        """Randomize the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.uniform_constrained(order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.uniform_constrained(radius_constraint)
        scale_constraint = cpool.get(self, SCALE_CONSTRAINT)
        self.scale = model_random.uniform_constrained(scale_constraint)
        dim_out_constraint = cpool.get(self, DIM_OUT_CONSTRAINT)
        self.dim_out = model_random.uniform_constrained(dim_out_constraint)

    def mutate(self):
        """Make small random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.jitter_constrained(self.order, order_constraint)
        radius_constraint = cpool.get(self, RADIUS_CONSTRAINT)
        self.radius = model_random.jitter_constrained(self.radius, radius_constraint)
        scale_constraint = cpool.get(self, SCALE_CONSTRAINT)
        self.scale = model_random.jitter_constrained(self.scale, scale_constraint)
        dim_out_constraint = cpool.get(self, DIM_OUT_CONSTRAINT)
        self.dim_out = model_random.jitter_constrained(self.dim_out, dim_out_constraint)

    def swap_places(self):
        """Nothing to do."""

    def crossingover(self, other):
        """
        pre: isinstance(other, DiskStamp)
        pre: isinstance(self, DiskStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = DiskStamp(self.get_trunk(), -1)
        cross_sequence = model_random.crossing_sequence(4)
        new_one.order = self.order if cross_sequence[0] else other.order
        new_one.radius = self.radius if cross_sequence[1] else other.radius
        new_one.scale = self.scale if cross_sequence[2] else other.scale
        new_one.dim_out = self.dim_out if cross_sequence[3] else other.dim_out
        return new_one

    def set_stamp_extent(self, width, height):
        """Set extent of stamp. This stamps will ignore these parameters."""
        pass

    def render(self, ctx, point, state):
        """
        pre: ctx is not None
        pre: len(point) == 2
        """
        src = ctx.get_source()
#        print ctx.get_source(), isinstance(ctx.get_source(), cairo.SolidPattern)
        if isinstance(src, cairo.SolidPattern):
            rgba = src.get_rgba()
            dim = div = 1.0
            for dummy in xrange(1, int(math.floor(self.order))):
                ctx.set_source_rgba(rgba[0]*dim,
                                    rgba[1]*dim,
                                    rgba[2]*dim, rgba[3])
                ctx.arc(point[0], point[1],
                        self.radius*div, 0.0, 2.0*math.pi)
                ctx.fill()
                div *= self.scale
                dim *= self.dim_out
            ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])

    def explain(self):
        """
        post: len(__return__) == 3
        """
        str_dim_out = _('dim out: %4.3f') % self.dim_out
        str_scale = _('scale: %4.3f') % self.scale
        return _('Disk stamp: number of disks: ') + str(int(math.floor(self.order))) \
               + ', ' + str_dim_out \
               + ', ' + str_scale , \
               None, \
               None

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, DiskStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = DiskStamp(self.get_trunk(), -1)
        new_one.order = self.order
        new_one.radius = self.radius
        new_one.scale = self.scale
        new_one.dim_out = self.dim_out
        return new_one
