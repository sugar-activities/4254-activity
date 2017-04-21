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

import traceback
import sys
import random
import cairo

import ka_debug
import model_locus
import model_allele
import model_random

class BorderModifier(model_allele.Allele):
    """BorderModifier
    inv: 0.0 <= self.border_weight <= 0.5
    inv: self.border_alpha == 0.0 or self.border_alpha == 1.0 
    """
    constraint_wieght = (0.0, 0.5)

    def __init__(self, trunk):
        """Constructor for a simple modifier."""
        super(BorderModifier, self).__init__(trunk)
        self.border_weight = 0.25
        self.border_alpha = 1.0
        self.constraint_weight = (0.0, 0.5)

    def __eq__(self, other):
        """Equality based on same instance."""
        equal = isinstance(other, BorderModifier) \
                and self.border_weight == other.border_weight \
                and self.border_alpha == other.border_alpha
        return equal

    def randomize(self):
        """No member variables. Nothing to do."""
        self.border_weight = random.uniform(self.constraint_weight[0], self.constraint_weight[1])
        self.border_alpha = 1.0 if random.randint(0, 1) > 0 else 0.0

    def mutate(self):
        """No member variables. Nothing to do."""
        if model_random.is_mutating():
            self.border_weight = model_random.jitter_constrained(self.border_weight, self.constraint_weight)
        if model_random.is_mutating():
            self.border_alpha = 1.0 if random.randint(0, 1) > 0 else 0.0

    def swap_places(self):
        """Nothing to do."""

    def crossingover(self, other):
        """
        pre: isinstance(other, BorderModifier)
        pre: isinstance(self, BorderModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = BorderModifier(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(2)
        new_one.border_weight = self.border_weight if cross_sequence[0] else other.border_weight
        new_one.border_alpha = self.border_alpha if cross_sequence[1] else other.border_alpha
        return new_one

    def render_single_layer(self, task, single_layer, single_treenode, ctx, width, height):
        """
        pre: single_layer is not None
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        try:
            # paint one layer
            msk_surface = ctx.get_target().create_similar(cairo.CONTENT_ALPHA, 
                                                          width, height)
            msk_ctx = cairo.Context(msk_surface)
            msk_width  = msk_surface.get_width()
            msk_height = msk_surface.get_height()
    
            # fill the whole background with an alpha value. 
            msk_ctx.set_operator(cairo.OPERATOR_SOURCE)
            msk_ctx.set_source_rgba(1.0, 1.0, 1.0, self.border_alpha)
            msk_ctx.paint()
    
            # fill the interior with an alpha value. 
            msk_ctx.set_operator(cairo.OPERATOR_SOURCE)
            msk_ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0-self.border_alpha)
            msk_ctx.rectangle(self.border_weight*msk_width,
                              self.border_weight*msk_height, 
                              (1.0-2.0*self.border_weight)*msk_width,
                              (1.0-2.0*self.border_weight)*msk_height)
            msk_ctx.fill()
            ctx.save()
#            ka_debug.matrix_s(ctx.get_matrix())
            single_layer.render(task, ctx, width, height)
#            msk_surface.write_to_png('/dev/shm/mask_' + self.get_unique_id() + '.png')
            ctx.mask_surface(msk_surface, -0.5*width, -0.5*height)
            single_treenode.render(task, ctx, width, height)
#            ka_debug.matrix_r(ctx.get_matrix())
            ctx.restore()
        except:
            ka_debug.err('failed calculating [%s] [%s] [%s]' % \
                   (self.get_unique_id(), sys.exc_info()[0], sys.exc_info()[1]))
            traceback.print_exc(file=sys.__stderr__)
#            ka_debug.matrix(ctx.get_matrix())


    def explain(self, task, formater, single_layer, single_treenode):
        formater.text_item(_('Border modifier, border weight=')
                           + unicode(self.border_weight) \
                           + _(' alpha=') + unicode(self.border_alpha))
        single_layer.explain(formater)
        single_treenode.explain(task, formater)

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, BorderModifier)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = BorderModifier(self.get_trunk())
        new_one.border_weight = self.border_weight
        new_one.border_alpha = self.border_alpha
        return new_one
