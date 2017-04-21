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
import cairo

import ka_debug
import model_random
import model_allele
import model_constraintpool

# Cairo's compositing operators 
#    OPERATOR_ADD = 12
#    OPERATOR_ATOP = 5
#    OPERATOR_CLEAR = 0
#    OPERATOR_DEST = 6
#    OPERATOR_DEST_ATOP = 10
#    OPERATOR_DEST_IN = 8
#    OPERATOR_DEST_OUT = 9
#    OPERATOR_DEST_OVER = 7
#    OPERATOR_IN = 3
#    OPERATOR_OUT = 4
#    OPERATOR_OVER = 2
#    OPERATOR_SATURATE = 13
#    OPERATOR_SOURCE = 1
#    OPERATOR_XOR = 11

OPERATOR_CONSTRAINT = 'operatorconstraint'
ALPHABLENDING_CONSTRAINT = 'alphaconstraint'

class MaskMerger(model_allele.Allele):
    """MaskMerger
    inv: cairo.OPERATOR_CLEAR <= self.left_operator <= cairo.OPERATOR_SATURATE
    """

    cdef = [{'bind'  : OPERATOR_CONSTRAINT,
                  'name'  : 'Permitted operators for combining two layers',
                  'domain': model_constraintpool.INT_M_OF_N,
                  'enum'  : [('add',  cairo.OPERATOR_ADD),
                            ('atop',  cairo.OPERATOR_ATOP),
# not usable                ('clear',  cairo.OPERATOR_CLEAR),
# not usable                ('destination',  cairo.OPERATOR_DEST),
                            ('destination atop',  cairo.OPERATOR_DEST_ATOP),
                            ('destination in',  cairo.OPERATOR_DEST_IN),
                            ('destination out',  cairo.OPERATOR_DEST_OUT),
# not usable                ('destination over',  cairo.OPERATOR_DEST_OVER),
# not usable                ('in',  cairo.OPERATOR_IN),
                            ('out',  cairo.OPERATOR_OUT),
                            ('over',  cairo.OPERATOR_OVER),
# not usable                             ('saturate',  cairo.OPERATOR_SATURATE),
                            ('source',  cairo.OPERATOR_SOURCE),
                            ('xor',  cairo.OPERATOR_XOR),],},
            {'bind'  : ALPHABLENDING_CONSTRAINT,
             'name'  : 'Alpha blending for combining layers.',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.75, 'max': 1.0},
           ]

    OPERATORS = [o[1] for o in cdef[0]['enum']]
    OPERATOR_NAMES = {}
    for o in cdef[0]['enum']:
        OPERATOR_NAMES[o[1]] = o[0]

    def __init__(self, trunk):
        """Constructor for a simple merger."""
        super(MaskMerger, self).__init__(trunk)
        self.left_operator = cairo.OPERATOR_ADD
        self.left_alphablending = 1.0

    def __eq__(self, other):
        """Randomize the mergers components."""
        equal = isinstance(other, MaskMerger) \
                and self.left_operator == other.left_operator \
                and self.left_alphablending == other.left_alphablending
        return equal

    def randomize(self):
        """No member variables. Nothing to do."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        operator_constraint = cpool.get(self, OPERATOR_CONSTRAINT)
        self.left_operator = random.choice(operator_constraint)
        alphablending_constraint = cpool.get(self, ALPHABLENDING_CONSTRAINT)
        self.left_alphablending = \
                    model_random.uniform_constrained(alphablending_constraint)

    def mutate(self):
        """Make random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        operator_constraint = cpool.get(self, OPERATOR_CONSTRAINT)
        if model_random.is_mutating():
            self.left_operator = random.choice(operator_constraint)
        alphablending_constraint = cpool.get(self, ALPHABLENDING_CONSTRAINT)
        self.left_alphablending = \
                    model_random.jitter_constrained(self.left_alphablending, \
                                                    alphablending_constraint)

    def swap_places(self):
        """Shuffle similar components."""
        pass

    def crossingover(self, other):
        """
        pre: isinstance(self, MaskMerger)
        pre: isinstance(other, MaskMerger)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = MaskMerger(self.get_trunk())
        crossing = model_random.crossing_sequence(4)
        new_one.left_operator = other.left_operator if crossing[0] \
                                                   else self.left_operator
        new_one.left_alphablending = other.left_alphablending if crossing[2] \
                                                   else self.left_alphablending
        return new_one

    def merge_layers(self, left_surface, right_surface, ctx, width, height):
        """
        pre: left_surface is not None
        pre: right_surface is not None
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        # draw 'left' layer using 'right' layer as mask
        ctx.set_operator(self.left_operator)
        ctx.translate(-0.5, -0.5)
#        ka_debug.matrix(ctx.get_matrix())
        ctx.scale(1.0/width, 1.0/height)
#        ka_debug.matrix(ctx.get_matrix())
        ctx.mask_surface(right_surface, 0, 0)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.set_source_surface(left_surface)
#        ka_debug.matrix(ctx.get_matrix())
        ctx.paint_with_alpha(self.left_alphablending) # 0.5 .. 1.0
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain_left(self, formater):
        formater.text_item(_('Compositing drawing operator for left node: ') \
                           + self.OPERATOR_NAMES[self.left_operator])
        formater.text_item(_('Alpha blending of left node: ') \
                           + str(self.left_alphablending))

    def explain_right(self, formater):
        formater.text_item(_('Compositing used right node as a mask surface.'))

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, MaskMerger)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = MaskMerger(self.get_trunk())
        new_one.left_operator = self.left_operator
        new_one.left_alphablending = self.left_alphablending
        return new_one
