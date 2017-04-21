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
import ka_factory
import model_locus
import model_layer
import model_constraintpool

PROBABILITY_CONSTRAINT = 'probabilityconstaint'
DEPTH_CONSTRAINT = 'depthconstraint'
BORDER_WIDTH_CONSTRAINT = 'borderwidthconstraint'
COLORGAMUTTYPE_CONSTRAINT = 'colorgamuttypeconstraint'

class QuadTreeLayer(model_layer.Layer):
    """QuadTreeLayer
    inv: len(self.tile_colors) > 0
    inv: self.depth  > 0
    """

    cdef = [{'bind'  : PROBABILITY_CONSTRAINT,
             'name'  : 'Probability of stepping one recursion deeper',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.0, 'max': 1.0},
            {'bind'  : DEPTH_CONSTRAINT,
             'name'  : 'Maximum recursion depth for quadtree',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 5},
            {'bind'  : BORDER_WIDTH_CONSTRAINT,
             'name'  : 'Width of the surrounding border',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.001, 'max': 0.1},
            {'bind'  : COLORGAMUTTYPE_CONSTRAINT,
             'name'  : 'Permitted color gamut',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('colorgamut').keys()},
           ]

    def __init__(self, trunk):
        """Quad tree layer constructor"""
        super(QuadTreeLayer, self).__init__(trunk)
        self.depth = 1
        self.propability = 0.5
        self.border_width = 0.01
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamut_key = colorgamut_factory.keys()[0]
        self.colorgamut = colorgamut_factory.create(colorgamut_key, self.path)

        self.tile_colors = [self.colorgamut.get_randomized_color(self.path)]

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.tile_colors:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality """
        equal = isinstance(other, QuadTreeLayer) \
                and model_layer.Layer.__eq__(self, other) \
                and len(self.tile_colors) == len(other.tile_colors) \
                and self.depth == other.depth \
                and self.propability == other.propability \
                and self.border_width == other.border_width
        if equal:
            for index, site_color in enumerate(self.tile_colors):
                equal = equal and site_color == other.tile_colors[index]
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(QuadTreeLayer, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        depth_constraint = cpool.get(self, DEPTH_CONSTRAINT)
        self.depth = model_random.randint_constrained(depth_constraint)
        
        border_width_constraint = cpool.get(self, BORDER_WIDTH_CONSTRAINT)
        self.border_width = model_random.uniform_constrained(border_width_constraint)

        propability_constraint = cpool.get(self, PROBABILITY_CONSTRAINT)
        self.propability = model_random.uniform_constrained(propability_constraint)
        
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
        self.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                           self.path)
        self.colorgamut.randomize()

        self.tile_colors = []
        for dummy in range(self.depth):
            site_color = self.colorgamut.get_randomized_color(self.path)
            self.tile_colors.append(site_color)

    def mutate(self):
        """Make small random changes to the layers components."""
        super(QuadTreeLayer, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        depth_constraint = cpool.get(self, DEPTH_CONSTRAINT)
        self.depth = model_random.jitter_discret_constrained(
                                                  self.depth, depth_constraint)
        propability_constraint = cpool.get(self, PROBABILITY_CONSTRAINT)
        self.propability = model_random.jitter_constrained(self.propability,
                                                           propability_constraint)

        border_width_constraint = cpool.get(self, BORDER_WIDTH_CONSTRAINT)
        self.border_width = model_random.jitter_constrained(self.border_width,
                                                            border_width_constraint)

        self.colorgamut.mutate()
        new_site_color = self.colorgamut.get_randomized_color(self.path)
        model_random.mutate_list(self.tile_colors,
                                 depth_constraint, new_site_color)
        for cix in range(len(self.tile_colors)):
            self.colorgamut.adjust_color(self.tile_colors[cix])

    def swap_places(self):
        """Shuffle similar components."""
        model_random.swap_places(self.tile_colors)

    def crossingover(self, other):
        """
        pre: isinstance(other, QuadTreeLayer)
        pre: isinstance(self, QuadTreeLayer)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = QuadTreeLayer(self.get_trunk())
        cross_sequence = self.crossingover_base(new_one, other, 4)
        new_one.depth = self.depth if cross_sequence[0] \
                                               else other.depth
        new_one.propability = self.propability if cross_sequence[1] \
                                               else other.propability
        new_one.border_width = self.border_width if cross_sequence[2] \
                                               else other.border_width
        new_one.colorgamut = other.colorgamut.copy() if cross_sequence[3] \
                                                     else self.colorgamut.copy() 
        new_one.tile_colors = model_random.crossingover_list(self.tile_colors,
                                                             other.tile_colors)
        for cix in range(len(new_one.tile_colors)):
            new_one.colorgamut.adjust_color(new_one.tile_colors[cix])

        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        self.begin_render(ctx, width, height)
        cell_rand = random.Random(self.random_seed)
        self.render_tile(task, ctx, cell_rand, self.depth, -0.5, -0.5, 1.0, 1.0)
        
    def render_tile(self, task, ctx, cell_rand, depth, x, y, width, height):
        next_depth = depth-1
        rgba = self.tile_colors[next_depth % len(self.tile_colors)].rgba
        ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        ctx.rectangle(x, y, width, height)
        ctx.fill()
        if depth > 0 and not task.quit \
           and cell_rand.random() < self.propability:
            width2, height2 = 0.5*width, 0.5*height
            self.render_tile(task, ctx, cell_rand, next_depth,
                             x, y, width2, height2)
            self.render_tile(task, ctx, cell_rand, next_depth,
                             x+width2, y, width2, height2)
            self.render_tile(task, ctx, cell_rand, next_depth,
                             x, y+height2, width2, height2)
            self.render_tile(task, ctx, cell_rand, next_depth,
                             x+width2, y+height2, width2, height2)
        ctx.set_line_width((width + height) * self.border_width)
        ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        ctx.rectangle(x, y, width, height)
        ctx.stroke()

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(QuadTreeLayer, self).explain(formater)
        formater.text_item(_('Probability of stepping one recursion step deeper: ')
                           + str(self.propability))
        formater.text_item(_('Maximum recursion depth: ')
                           + str(self.depth))
        formater.text_item(_('Width of the surrounding border: ')
                           + str(self.border_width))
        self.colorgamut.explain(formater)
        formater.color_array(self.tile_colors, _('Site colors:'))
        formater.end_list()

    def copy(self):
        """The Quad tree layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = QuadTreeLayer(self.get_trunk())
        self.copy_base(new_one)
        new_one.tile_colors = model_random.copy_list(self.tile_colors)
        new_one.propability = self.propability
        new_one.depth = self.depth
        new_one.border_width = self.border_width
        new_one.colorgamut = self.colorgamut.copy()
        return new_one
