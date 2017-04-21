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

class FlipModifier(model_allele.Allele):
    """FlipModifier: Reverse the layer horizontally or vertically.
    inv: self.xFlip == -1.0 or self.xFlip == 1.0 
    inv: self.yFlip == -1.0 or self.yFlip == 1.0 
    """

    def __init__(self, trunk):
        """Constructor for a flip modifier."""
        super(FlipModifier, self).__init__(trunk)
        self.xFlip = 1.0
        self.yFlip = 1.0

    def __eq__(self, other):
        """Equality based on fliping horizontally or vertically."""
        equal = isinstance(other, FlipModifier) \
                and self.xFlip == other.xFlip \
                and self.yFlip == other.yFlip
        return equal

    def randomize(self):
        """Randomize the layers components."""
        self.xFlip = 1.0 if random.randint(0, 1) > 0 else -1.0
        self.yFlip = 1.0 if random.randint(0, 1) > 0 else -1.0

    def mutate(self):
        """Make small random changes to the layers components."""
        if model_random.is_mutating():
            self.xFlip = 1.0 if random.randint(0, 1) > 0 else -1.0
        if model_random.is_mutating():
            self.yFlip = 1.0 if random.randint(0, 1) > 0 else -1.0

    def swap_places(self):
        """Exchange x and y flip."""
        self.xFlip, self.yFlip = model_random.swap_parameters(self.xFlip,
                                                              self.yFlip)

    def crossingover(self, other):
        """
        pre: isinstance(other, FlipModifier)
        pre: isinstance(self, FlipModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = FlipModifier(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(2)
        new_one.xFlip = self.xFlip if cross_sequence[0] else other.xFlip
        new_one.yFlip = self.yFlip if cross_sequence[1] else other.yFlip
        return new_one

    def render_single_layer(self, task, single_layer, single_treenode, ctx, width, height):
        """
        pre: single_layer is not None
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        # paint one layer
        ctx.scale(self.xFlip, self.yFlip)
#        ka_debug.matrix(ctx.get_matrix())
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        single_layer.render(task, ctx, width, height)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()
        single_treenode.render(task, ctx, width, height)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain(self, task, formater, single_layer, single_treenode):
        if self.xFlip < 0.0 and self.yFlip < 0.0:
            text = _('Flip modifier: flip horizontally and vertically.') 
        elif self.xFlip < 0.0:
            text = _('Flip modifier: flip horizontally.')
        elif self.yFlip < 0.0:
            text = _('Flip modifier: flip vertically.')
        else:
            text = _('Flip modifier: did not flip.')
        formater.text_item(text)
        single_layer.explain(formater)
        single_treenode.explain(task, formater)
        
    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, FlipModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = FlipModifier(self.get_trunk())
        new_one.xFlip = self.xFlip
        new_one.yFlip = self.yFlip
        return new_one
