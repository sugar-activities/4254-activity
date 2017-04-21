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
import math
import cairo

import ka_debug
import ka_extensionpoint
import model_random
import model_constraintpool
import model_locus
import model_allele

EPSILON = 0.00001
DIRECTION_CONSTRAINT = 'directionconstraint'

class Direction(model_allele.Allele):
    """ Direction. A vector in the x-y plane.
    The vector is defined by angle and radius.
    """

    cdef = [{'bind'  : DIRECTION_CONSTRAINT,
             'name'  : 'Direction constraint',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_extensionpoint.list_extensions(DIRECTION_CONSTRAINT)
            },
           ]

    def __init__(self, trunk, radian, offset):
        """Direction constructor
        """
        super(Direction, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraint_name = cpool.get(self, DIRECTION_CONSTRAINT)[0]
        self.constraint = ka_extensionpoint.create(constraint_name, self.path)
        self.radian, self.offset = self.constraint.filter(radian, offset)
        
    def __eq__(self, other):
        """Equality based on radian and offset."""
        return isinstance(other, Direction) \
               and abs(self.radian - other.radian) < EPSILON \
               and abs(self.offset - other.offset) < EPSILON

    def randomize(self):
        """Set radian and offset to random values."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraints = cpool.get(self, DIRECTION_CONSTRAINT)
        self.constraint = ka_extensionpoint.create(random.choice(constraints),
                                                                     self.path)
        self.radian, self.offset = self.constraint.randomize()

    def mutate(self):
        """Make small random changes in radian and offset."""
        if model_random.is_mutating():
            if model_random.is_mutating():
                cpool = model_constraintpool.ConstraintPool.get_pool()
                constraints = cpool.get(self, DIRECTION_CONSTRAINT)
                self.constraint = ka_extensionpoint.create(
                                         random.choice(constraints), self.path)
            self.radian, self.offset = self.constraint.mutate(self.radian,
                                                              self.offset)

    def swap_places(self):
        """Not implemented."""

    def crossingover(self, other):
        """Returns either a copy of self or a copy of other.
        pre: isinstance(other, Direction)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        randseq = model_random.crossing_sequence(1)
        return self.copy() if randseq[0] else other.copy()

    def copy(self):
        """A direction copy constructor
        post: isinstance(__return__, Direction)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = Direction(self.get_trunk(), 0.0, 0.0)
        new_one.radian, new_one.offset = self.radian, self.offset
        new_one.constraint = self.constraint
        return new_one

    def explain(self):
        """Returns a string describing details."""
        return '%4.3f, %4.3f' % (self.radian, self.offset)

    @staticmethod
    def make_icon(direction_list, width, height):
        """Calculate an icon visualizing the direction vectors"""
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.scale(float(width), float(height))
#        ka_debug.matrix(ctx.get_matrix())
        # paint background
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.paint()
        ctx.set_line_width(0.02)
        for direction in direction_list:
            # paint a arrow for each direction
            delta_x = direction.offset * math.cos(direction.radian)
            delta_y = direction.offset * math.sin(direction.radian)
            ctx.set_source_rgb(0.0, 0.0, 0.0)
            ctx.move_to(0.5, 0.5)
            ctx.line_to(0.5+delta_x, 0.5+delta_y)
            ctx.stroke()
        return surface
