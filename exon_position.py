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
import cairo

import ka_debug
import ka_extensionpoint
import model_random
import model_constraintpool
import model_locus
import model_allele

EPSILON = 0.00001
POSITION_CONSTRAINT = 'positionconstraint'

class Position(model_allele.Allele):
    """Position
    """

    cdef = [{'bind'  : POSITION_CONSTRAINT,
             'name'  : 'Position',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_extensionpoint.list_extensions(POSITION_CONSTRAINT)
            },
           ]

    def __init__(self, trunk, x_pos, y_pos):
        """Position constructor
        """
        super(Position, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraint_name = cpool.get(self, POSITION_CONSTRAINT)[0]
        self.constraint = ka_extensionpoint.create(constraint_name, self.path)
        self.x_pos, self.y_pos = self.constraint.filter(x_pos, y_pos)
        
    def __eq__(self, other):
        """Equality based on color components."""
        return isinstance(other, Position) \
               and abs(self.x_pos - other.x_pos) < EPSILON \
               and abs(self.y_pos - other.y_pos) < EPSILON

    def randomize(self):
        """Set x_pos, y_pos to random values."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraints = cpool.get(self, POSITION_CONSTRAINT)
        self.constraint = ka_extensionpoint.create(random.choice(constraints),
                                                   self.path)
        self.x_pos, self.y_pos = self.constraint.randomize()

    def mutate(self):
        """Make small random changes in position."""
        if model_random.is_mutating():
            if model_random.is_mutating():
                cpool = model_constraintpool.ConstraintPool.get_pool()
                constraints = cpool.get(self, POSITION_CONSTRAINT)
                self.constraint = ka_extensionpoint.create(
                                         random.choice(constraints), self.path)
            self.x_pos, self.y_pos = self.constraint.mutate(self.x_pos,
                                                            self.y_pos)

    def swap_places(self):
        """Exchange x- and y-tiles."""
        self.x_pos, self.y_pos = model_random.swap_parameters(self.x_pos,
                                                           self.y_pos)

    def crossingover(self, other):
        """Returns either a copy of self or a copy of other.
        pre: isinstance(other, Position)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        randseq = model_random.crossing_sequence(1)
        return self.copy() if randseq[0] else other.copy()

    def copy(self):
        """A position copy constructor
        post: isinstance(__return__, Position)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = Position(self.get_trunk(), 0.0, 0.0)
        new_one.x_pos, new_one.y_pos = self.x_pos, self.y_pos
        new_one.constraint = self.constraint
        return new_one

    def explain(self):
        """Returns a string describing details."""
        return '%4.3f, %4.3f' % (self.x_pos, self.y_pos)

    @staticmethod
    def make_icon(position_list, width, height):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.scale(float(width), float(height))
#        ka_debug.matrix(ctx.get_matrix())
        # paint background
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.paint()
        radius = 0.1
        ctx.set_line_width(0.02)
        for position in position_list:
            # paint a cross for each position
            ctx.set_source_rgb(0.0, 0.0, 0.0)
            ctx.move_to(position.x_pos-radius, position.y_pos-radius)
            ctx.line_to(position.x_pos+radius, position.y_pos+radius)
            ctx.move_to(position.x_pos+radius, position.y_pos-radius)
            ctx.line_to(position.x_pos-radius, position.y_pos+radius)
            ctx.stroke()
        return surface
