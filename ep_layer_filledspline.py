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

import model_random

from gettext import gettext as _

import ka_debug
import ka_factory
import model_locus
import model_layer
import model_constraintpool
import exon_position
SAMPLERTYPE_CONSTRAINT = 'samplertypeconstraint'
COLORGAMUTTYPE_CONSTRAINT = 'colorgamuttypeconstraint'

class FilledSpline(model_layer.Layer):
    """FilledSpline
    """

    cdef = [{'bind'  : 'length',
             'name'  : 'Number of interpolation points',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 4, 'max': 32},
            {'bind'  : 'line_width',
             'name'  : 'Line width',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.001, 'max': 0.25},
            {'bind'  : 'roundness',
             'name'  : 'Roundness of spline',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.1, 'max': 20.0},
            {'bind'  : SAMPLERTYPE_CONSTRAINT,
             'name'  : 'Permitted sampler types',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('sampler').keys()},
            {'bind'  : COLORGAMUTTYPE_CONSTRAINT,
             'name'  : 'Permitted color gamut',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('colorgamut').keys()},
           ]

    def __init__(self, trunk):
        """FilledSpline diagram layer constructor"""
        super(FilledSpline, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamut_key = colorgamut_factory.keys()[0]
        self.colorgamut = colorgamut_factory.create(colorgamut_key, self.path)
        self.linecolor = self.colorgamut.get_randomized_color(self.path)
        self.fillcolor = self.colorgamut.get_randomized_color(self.path)
        self.line_width = cpool.get(self, 'line_width')[0]
        self.roundness = cpool.get(self, 'roundness')[0]
        self.center = exon_position.Position(self.path, 0.0, 0.0)
        sampler_factory = ka_factory.get_factory('sampler')
        sampler_key = sampler_factory.keys()[0]
        self.sampler = sampler_factory.create(sampler_key, self.path)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.colorgamut, self.linecolor, self.fillcolor, self.center, self.sampler]:
            result += ka_debug.dot_ref(anchor, ref)
        return result

    def __eq__(self, other):
        """Equality based on the objects components."""
        equal = isinstance(other, FilledSpline) \
                and super(FilledSpline, self).__eq__(other) \
                and self.linecolor == other.linecolor \
                and self.fillcolor == other.fillcolor \
                and self.line_width == other.line_width \
                and self.roundness == other.roundness \
                and self.center == other.center \
                and self.sampler == other.sampler \
                and self.colorgamut == other.colorgamut
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(FilledSpline, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        line_width_constraint = cpool.get(self, 'line_width')
        roundness_constraint = cpool.get(self, 'roundness')
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
        self.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                           self.path)
        self.colorgamut.randomize()
        self.linecolor = self.colorgamut.get_randomized_color(self.path)
        self.fillcolor = self.colorgamut.get_randomized_color(self.path)
        self.line_width = model_random.uniform_constrained(line_width_constraint)
        self.roundness = model_random.uniform_constrained(roundness_constraint)
        self.center.randomize()
        sampler_factory = ka_factory.get_factory('sampler')
        samplertype_constraint = cpool.get(self, SAMPLERTYPE_CONSTRAINT)
        self.sampler = sampler_factory.create_random(samplertype_constraint, 
                                                     self.path)
        self.sampler.randomize()

    def mutate(self):
        """Make small random changes to the layers components."""
        super(FilledSpline, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        line_width_constraint = cpool.get(self, 'line_width')
        roundness_constraint = cpool.get(self, 'roundness')
        self.colorgamut.mutate()
        self.colorgamut.adjust_color(self.linecolor)
        self.colorgamut.adjust_color(self.fillcolor)
        self.line_width = model_random.jitter_constrained(self.line_width, line_width_constraint)
        self.roundness = model_random.jitter_constrained(self.roundness, roundness_constraint)
        self.center.mutate()
        self.sampler.mutate()

    def swap_places(self):
        """Shuffle similar components."""
        self.center.swap_places()
        self.sampler.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, FilledSpline)
        pre: isinstance(self, FilledSpline)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = FilledSpline(self.get_trunk())
        crossing = self.crossingover_base(new_one, other, 3)
        if crossing[0]:
            new_one.colorgamut = other.colorgamut.copy() 
            new_one.linecolor = other.linecolor.copy()
            new_one.fillcolor = other.fillcolor.copy()
        else:
            new_one.colorgamut = self.colorgamut.copy() 
            new_one.linecolor = self.linecolor.copy()
            new_one.fillcolor = self.fillcolor.copy()
        new_one.line_width = other.line_width if crossing[1] else self.line_width
        new_one.roundness = other.roundness if crossing[2] else self.roundness
        new_one.center = self.center.crossingover(other.center)
        new_one.sampler = model_random.crossingover_elem(self.sampler,
                                                         other.sampler)
        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        self.begin_render(ctx, width, height)

        px, py = self.center.x_pos, self.center.y_pos
        ctx.move_to(px, py)
        points = self.sampler.get_sample_points()
        for index in xrange(len(points)):
            if index == 0:
                pass
            elif index == 1:
                ctx.move_to(px+points[index][0], py+points[index][1])
            elif index == len(points)-1:
                pass
            else:
                end_x, end_y = points[index][0], points[index][1]
                cstart_x = points[index-1][0] - self.roundness * (points[index-1][0]-points[index-2][0])
                cstart_y = points[index-1][1] - self.roundness * (points[index-1][1]-points[index-2][1])
                cend_x   = end_x + self.roundness * (points[index+1][0]-end_x)
                cend_y   = end_y + self.roundness * (points[index+1][1]-end_y)
#                cstart_x = (points[index-1][0]+points[index-2][0])
#                cstart_y = (points[index-1][1]+points[index-2][1])
#                cend_x   = (points[index+1][0]+end_x)
#                cend_y   = (points[index+1][1]+end_y)
                ctx.curve_to (px+cend_x,   py+cend_y,   # end control point
                              px+cstart_x, py+cstart_y, # start control point
                              px+end_x,    py+end_y)    # end point
#        print str(ctx.copy_path())
        rgba = self.fillcolor.rgba
        ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        ctx.fill_preserve()
        ctx.set_line_width(self.line_width)
        rgba = self.linecolor.rgba
        ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        ctx.stroke()
        
    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(FilledSpline, self).explain(formater)
        self.colorgamut.explain(formater)
        formater.color_item(self.linecolor, _('line color:'))
        formater.text_item(_('line width: ') + str(self.line_width))
        formater.text_item(_('roundness: ') + str(self.roundness))
        formater.color_item(self.fillcolor, _('fill color:'))
        formater.position_item(self.center, _('center:'))
        text, surface, descr = self.sampler.explain()
        if surface is not None:
            formater.surface_item(surface, _('sampling points: ') + text, descr)
        else:
            formater.text_item(text)
        formater.end_list()

    def copy(self):
        """The FilledSpline diagram layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = FilledSpline(self.get_trunk())
        self.copy_base(new_one)
        new_one.linecolor = self.linecolor.copy()
        new_one.fillcolor = self.fillcolor.copy()
        new_one.line_width = self.line_width
        new_one.roundness = self.roundness
        new_one.center = self.center.copy()
        new_one.sampler = self.sampler.copy()
        # upgrade from a release older than 'v4'
        if self.__dict__.has_key('colorgamut'):
            new_one.colorgamut = self.colorgamut.copy()
        else:
            cpool = model_constraintpool.ConstraintPool.get_pool()
            colorgamut_factory = ka_factory.get_factory('colorgamut')
            colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
            new_one.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                                  new_one.path)
            new_one.colorgamut.randomize()
        return new_one
