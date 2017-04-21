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
import random
import cairo

import ka_debug
import model_random
import model_locus
import model_allele
import exon_position
import exon_direction

class MaskModifier(model_allele.Allele):
    """MaskModifier
    """

    def __init__(self, trunk):
        """Constructor for a simple modifier."""
        super(MaskModifier, self).__init__(trunk)
        self.alpha1 = 1.0
        self.alpha2 = 0.0
        self.center = exon_position.Position(self.path, 0.0, 0.0)
        self.direction = exon_direction.Direction(self.path, 0.0, 0.0)
        self.constraint_alpha = (0.0, 1.0)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.center, self.direction]:
            result += ka_debug.dot_ref(anchor, ref)
        return result

    def __eq__(self, other):
        """Equality based on same instance and the modifiers components."""
        equal = isinstance(other, MaskModifier) \
                and self.alpha1 == other.alpha1 \
                and self.alpha2 == other.alpha2 \
                and self.center == other.center \
                and self.direction == other.direction
        return equal

    def randomize(self):
        """Randomize the modifiers components."""
        self.alpha1 = random.uniform(self.constraint_alpha[0],
                                    self.constraint_alpha[1])
        self.alpha2 = random.uniform(self.constraint_alpha[0],
                                    self.constraint_alpha[1])
        self.center.randomize()
        self.direction.randomize()

    def mutate(self):
        """Mutate the modifiers components"""
        if model_random.is_mutating():
            self.alpha1 = model_random.jitter_constrained(self.alpha1, self.constraint_alpha)
        if model_random.is_mutating():
            self.alpha2 = model_random.jitter_constrained(self.alpha2, self.constraint_alpha)
        self.center.mutate()
        self.direction.mutate()

    def swap_places(self):
        """
        """
        self.alpha1, self.alpha2 = model_random.swap_parameters(self.alpha1,
                                                                self.alpha2)
        self.center.swap_places()
        self.direction.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, MaskModifier)
        pre: isinstance(self, MaskModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = MaskModifier(self.get_trunk())
        crossing = model_random.crossing_sequence(2)
        new_one.alpha1 = other.alpha1 if crossing[0] else self.alpha1
        new_one.alpha2 = other.alpha2 if crossing[0] else self.alpha2
        new_one.center = self.center.crossingover(other.center)
        new_one.direction = self.direction.crossingover(other.direction)
        return new_one

    def render_single_layer(self, task, single_layer, single_treenode, ctx, width, height):
        """
        pre: single_layer is not None
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        # paint masked by an linear gradient
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())

        delta_x = self.direction.offset * math.cos(self.direction.radian)
        delta_y = self.direction.offset * math.sin(self.direction.radian)
        linear = cairo.LinearGradient(self.center.x_pos + delta_x - 0.5,
                                      self.center.y_pos + delta_y - 0.5,
                                      self.center.x_pos - delta_x - 0.5,
                                      self.center.y_pos - delta_y - 0.5)
        linear.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, self.alpha1)
        linear.add_color_stop_rgba(0.0, 0.0, 0.0, 0.0, self.alpha2)
     
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        single_layer.render(task, ctx, width, height)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()
        ctx.mask(linear)
        single_treenode.render(task, ctx, width, height)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain(self, task, formater, single_layer, single_treenode):
        formater.text_item(_('Mask modifier, center=') + self.center.explain() \
               + _(' direction=') + self.direction.explain()
               + _(' alpha1=') + unicode(self.alpha1)
               + _(' alpha2=') + unicode(self.alpha2))
        single_layer.explain(formater)
        single_treenode.explain(task, formater)
        
    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, MaskModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = MaskModifier(self.get_trunk())
        new_one.center = self.center.copy()
        new_one.direction = self.direction.copy()
        new_one.alpha1 = self.alpha1
        new_one.alpha2 = self.alpha2
        return new_one
