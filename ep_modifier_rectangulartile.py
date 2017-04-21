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

import random

import ka_debug
import model_random
import model_locus
import model_allele

class RectangularTileModifier(model_allele.Allele):
    """RectangularTileModifier: Reverse the layer horizontally or vertically.
    inv: self.x_tiles > 0
    inv: self.y_tiles > 0
    """

    def __init__(self, trunk):
        """Constructor for a flip modifier."""
        super(RectangularTileModifier, self).__init__(trunk)
        self.x_tiles = 1
        self.y_tiles = 1

    def __eq__(self, other):
        """Equality based on fliping horizontally or vertically."""
        equal = isinstance(other, RectangularTileModifier) \
                and self.x_tiles == other.x_tiles \
                and self.y_tiles == other.y_tiles
        return equal

    def randomize(self):
        """Randomize the layers components."""
        self.x_tiles = random.randint(1, 3)
        self.y_tiles = random.randint(1, 3)

    def mutate(self):
        """Make small random changes to the layers components."""
        if model_random.is_mutating():
            self.x_tiles += random.randint(-1, 1)
            self.x_tiles = 1 if self.x_tiles < 1 else self.x_tiles
        if model_random.is_mutating():
            self.y_tiles += random.randint(-1, 1)
            self.y_tiles = 1 if self.y_tiles < 1 else self.y_tiles

    def swap_places(self):
        """Exchange x- and y-tiles."""
        self.x_tiles, self.y_tiles = model_random.swap_parameters(self.x_tiles,
                                                             self.y_tiles)

    def crossingover(self, other):
        """
        pre: isinstance(other, RectangularTileModifier)
        pre: isinstance(self, RectangularTileModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = RectangularTileModifier(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(2)
        new_one.x_tiles = self.x_tiles if cross_sequence[0] else other.x_tiles
        new_one.y_tiles = self.y_tiles if cross_sequence[1] else other.y_tiles
        return new_one

    def render_single_layer(self, task, single_layer, single_treenode, ctx, width, height):
        """
        pre: single_layer is not None
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        # repeat painting layer
        delta_x, delta_y  = 1.0 / self.x_tiles, 1.0 / self.y_tiles
        for tix in range(self.x_tiles):
            for tiy in range(self.y_tiles):
                if task.quit:
                    return
                ctx.save()
#                ka_debug.matrix_s(ctx.get_matrix())
                ctx.translate((tix-0.5*self.x_tiles)*delta_x+0.5*delta_x, \
                              (tiy-0.5*self.y_tiles)*delta_y+0.5*delta_y)
#                ka_debug.matrix(ctx.get_matrix())
                ctx.scale(delta_x, delta_y)
#                ka_debug.matrix(ctx.get_matrix())
                ctx.save()
                ka_debug.matrix_s(ctx.get_matrix())
                ctx.save()
#                ka_debug.matrix_s(ctx.get_matrix())
                single_layer.render(task, ctx, width, height)
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()
                single_treenode.render(task, ctx, width, height)
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()

    def explain(self, task, formater, single_layer, single_treenode):
        formater.text_item(_('Rectangular tile modifier: %d*x, %d*y')
                                               % (self.x_tiles, self.y_tiles))
        single_layer.explain(formater)
        single_treenode.explain(task, formater)
        

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, RectangularTileModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = RectangularTileModifier(self.get_trunk())
        new_one.x_tiles = self.x_tiles
        new_one.y_tiles = self.y_tiles
        return new_one
