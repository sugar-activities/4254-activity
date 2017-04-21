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
import ka_extensionpoint
import model_random
import model_constraintpool
import model_locus
import model_allele

EPSILON = 0.00001
COLOR_CONSTRAINT = 'colorconstraint'

class Color(model_allele.Allele):
    """Color
    inv: len(self.rgba) == 4
    inv: 0.0 <= self.rgba[0] <= 1.0
    inv: 0.0 <= self.rgba[1] <= 1.0
    inv: 0.0 <= self.rgba[2] <= 1.0
    inv: 0.0 <= self.rgba[3] <= 1.0
    """

    cdef = [{'bind'  : COLOR_CONSTRAINT,
             'name'  : 'Color constraint',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_extensionpoint.list_extensions(COLOR_CONSTRAINT)
            },
           ]

    def __init__(self, trunk, red, green, blue, alpha):
        """Color constructor
        pre: 0.0 <= red <= 1.0
        pre: 0.0 <= green <= 1.0
        pre: 0.0 <= blue <= 1.0
        pre: 0.0 <= alpha <= 1.0
        """
        super(Color, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraint_name = cpool.get(self, COLOR_CONSTRAINT)[0]
        self.constraint = ka_extensionpoint.create(constraint_name, self.path)
        self.rgba = self.constraint.filter((red, green, blue, alpha))
        self.base_diff_hue = 0 
        self.base_diff_lightness = 0 
        self.base_diff_saturation = 0 
        
    def __eq__(self, other):
        """Equality based on color components."""
        return isinstance(other, Color) \
               and abs(self.rgba[0] - other.rgba[0]) < EPSILON \
               and abs(self.rgba[1] - other.rgba[1]) < EPSILON \
               and abs(self.rgba[2] - other.rgba[2]) < EPSILON \
               and abs(self.rgba[3] - other.rgba[3]) < EPSILON

    def set_base_color(self, diff_hue, diff_lightness, diff_saturation):
        """Set optional base color.
        Only if this color depends on a 'leading' color."""
        self.base_diff_hue = diff_hue 
        self.base_diff_lightness = diff_lightness 
        self.base_diff_saturation = diff_saturation
 
    def randomize(self):
        """Set red, green, blue and alpha to random values."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        constraints = cpool.get(self, COLOR_CONSTRAINT)
        #TODO prefer a single constraint
        #TODO Remove pushing colorconstraint_none by a more generalized solution 
        if 'colorconstraint_none' in constraints and random.random() < 0.5:
            self.constraint = ka_extensionpoint.create(random.choice(['colorconstraint_none']),
                                                       self.path)
        else:
            self.constraint = ka_extensionpoint.create(random.choice(constraints),
                                                       self.path)
        self.rgba = self.constraint.randomize()

    def mutate(self):
        """Make small random changes in hue, lightness, saturation."""
        if model_random.is_mutating():
            if model_random.is_mutating():
                cpool = model_constraintpool.ConstraintPool.get_pool()
                constraints = cpool.get(self, COLOR_CONSTRAINT)
                self.constraint = ka_extensionpoint.create(
                                        random.choice(constraints), self.path)
            self.rgba = self.constraint.mutate(self.rgba)

    def swap_places(self):
        """Not implemented."""

    def crossingover(self, other):
        """Returns either a copy of self or a copy of other.
        pre: isinstance(other, Color)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        randseq = model_random.crossing_sequence(1)
        return self.copy() if randseq[0] else other.copy()

    def copy(self):
        """A color copy constructor
        post: isinstance(__return__, Color)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = Color(self.get_trunk(), 0.0, 0.0, 0.0, 0.0)
        new_one.rgba = (self.rgba[0], self.rgba[1], self.rgba[2], self.rgba[3])
        new_one.constraint = self.constraint
        # upgrade from a release older than 'v4'
        if self.__dict__.has_key('base_diff_hue'):
            new_one.base_diff_hue = self.base_diff_hue 
            new_one.base_diff_lightness = self.base_diff_lightness 
            new_one.base_diff_saturation = self.base_diff_saturation
        return new_one

    def explain(self, alpha=True):
        """Returns a string describing details."""
        return self.constraint.explain(self.rgba, alpha)

    @staticmethod
    def make_icon(rgba, alpha, width, height):
        """Calculate an icon filled with this color
        over a checker board to visualize transparency.
        """
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        if alpha:
            # paint checker board background
            steps = 4
            delta = (1.0 * width) / (1.0 * steps)
            ctx.set_operator(cairo.OPERATOR_SOURCE)
            for row in range(steps):
                for col in range(steps):
                    ctx.rectangle(col * delta, row * delta, delta, delta)
                    if (col + row) % 2 == 0:
                        ctx.set_source_rgb(0.4, 0.4, 0.4)
                    else:
                        ctx.set_source_rgb(0.6, 0.6, 0.6)
                    ctx.fill()
            # paint color and alpha
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        else:
            # paint color
            ctx.set_operator(cairo.OPERATOR_OVER)
            ctx.set_source_rgb(rgba[0], rgba[1], rgba[2])
        ctx.paint()
        return surface

