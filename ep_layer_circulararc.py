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

import ka_debug
import ka_factory
import model_locus
import model_layer
import model_random
import model_constraintpool
import exon_color
import math

LINE_WIDTH__CONSTRAINT = 'linewidthconstraint'
SIZE_CONSTRAINT        = 'sizeconstraint'
START_ANGLE_CONSTRAINT = 'startangleconstraint'
ANGLE_CONSTRAINT       = 'angleconstraint'
SAMPLERTYPE_CONSTRAINT = 'samplertypeconstraint'

class CircularArc(model_layer.Layer):
    """A layer with circular arcs
    """

    cdef = [{'bind'  : LINE_WIDTH__CONSTRAINT,
             'name'  : 'Specifies line width of the circle.',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 0.25},
            {'bind'  : SIZE_CONSTRAINT,
             'name'  : 'A factor for scaling the radius of the circle.',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.01, 'max': 1.0},
            {'bind'  : START_ANGLE_CONSTRAINT,
             'name'  : 'The start angle, in radians.',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.0, 'max': 2.0*math.pi},
            {'bind'  : ANGLE_CONSTRAINT,
             'name'  : 'The angle spawned by this arc, in radians.',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -3.0*math.pi, 'max': 3.0*math.pi},
            {'bind'  : SAMPLERTYPE_CONSTRAINT,
             'name'  : 'Permitted sampler types',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_factory.get_factory('sampler').keys()},
            ]

    def __init__(self, trunk):
        """CircularArc diagram layer constructor"""
        super(CircularArc, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.linecolor = exon_color.Color(self.path, 0, 0, 0, 1)
        self.line_width = cpool.get(self, LINE_WIDTH__CONSTRAINT)[0]
        self.size = cpool.get(self, SIZE_CONSTRAINT)[0]
        self.start_angle = cpool.get(self, START_ANGLE_CONSTRAINT)[0]
        self.angle = cpool.get(self, ANGLE_CONSTRAINT)[0]
        sampler_factory = ka_factory.get_factory('sampler')
        sampler_key = sampler_factory.keys()[0]
        self.sampler = sampler_factory.create(sampler_key, self.path)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.linecolor, self.sampler, ]:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality based on the objects components."""
        equal = isinstance(other, CircularArc) \
                and super(CircularArc, self).__eq__(other) \
                and self.linecolor == other.linecolor \
                and self.line_width == other.line_width \
                and self.size == other.size \
                and self.start_angle == other.start_angle \
                and self.angle == other.angle \
                and self.sampler == other.sampler
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(CircularArc, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.linecolor.randomize()
        line_width_constraint = cpool.get(self, LINE_WIDTH__CONSTRAINT)
        self.line_width = model_random.uniform_constrained(line_width_constraint)
        size_constraint = cpool.get(self, SIZE_CONSTRAINT)
        self.size = model_random.uniform_constrained(size_constraint)
        start_angle_constraint = cpool.get(self, START_ANGLE_CONSTRAINT)
        self.start_angle = model_random.uniform_constrained(start_angle_constraint)
        angle_constraint = cpool.get(self, ANGLE_CONSTRAINT)
        self.angle = model_random.uniform_constrained(angle_constraint)

        sampler_factory = ka_factory.get_factory('sampler')
        samplertype_constraint = cpool.get(self, SAMPLERTYPE_CONSTRAINT)
        self.sampler = sampler_factory.create_random(samplertype_constraint, 
                                                     self.path)
        self.sampler.randomize()

    def mutate(self):
        """Make small random changes to the layers components."""
        super(CircularArc, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.linecolor.mutate()
        line_width_constraint = cpool.get(self, LINE_WIDTH__CONSTRAINT)
        self.line_width = model_random.jitter_constrained(
                                         self.line_width, line_width_constraint)
        size_constraint = cpool.get(self, SIZE_CONSTRAINT)
        self.size = model_random.jitter_constrained(self.size, size_constraint)
        start_angle_constraint = cpool.get(self, START_ANGLE_CONSTRAINT)
        self.start_angle = model_random.jitter_constrained(self.start_angle, start_angle_constraint)
        angle_constraint = cpool.get(self, ANGLE_CONSTRAINT)
        self.angle = model_random.jitter_constrained(self.angle, angle_constraint)
        self.sampler.mutate()

    def swap_places(self):
        """Shuffle similar components."""
        self.sampler.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, CircularArc)
        pre: isinstance(self, CircularArc)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = CircularArc(self.get_trunk())
        crossing = self.crossingover_base(new_one, other, 4)
        new_one.linecolor = self.linecolor.crossingover(other.linecolor)
        new_one.line_width = self.line_width if crossing[0] else other.line_width
        new_one.size = self.size if crossing[1] else other.size
        new_one.start_angle = self.start_angle if crossing[2] else other.start_angle
        new_one.angle = self.angle if crossing[3] else other.angle
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
 
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        ctx.set_line_width(self.line_width)
        rgba = self.linecolor.rgba
        ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
        points = self.sampler.get_sample_points()
        for index, point in enumerate(points):
            nb2 = index+1
            if nb2 < len(points):
                radius = self.size*math.sqrt((points[nb2][0]-point[0])**2.0 \
                                             + (points[nb2][1]-point[1])**2.0)
                if self.angle > 2.0*math.pi or self.angle < -2.0*math.pi :
                    ctx.arc(point[0], point[1], radius, 0.0, 2.0*math.pi)
                elif self.angle > 0.0:
                    ctx.arc(point[0], point[1], radius,
                            self.start_angle, self.start_angle + self.angle)
                else:
                    ctx.arc_negative(point[0], point[1], radius,
                            self.start_angle, self.start_angle + self.angle)
                ctx.stroke()
            
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(CircularArc, self).explain(formater)
        formater.color_item(self.linecolor, _('line color:'))
        formater.text_item(_('line width: ') + str(self.line_width))
        formater.text_item(_('size: ') + str(self.size))
        formater.text_item(_('start angle: ') + str(self.start_angle))
        formater.text_item(_('angle: ') + str(self.angle))
        text, surface, descr = self.sampler.explain()
        if surface is not None:
            formater.surface_item(surface, _('sampling points: ') + text, descr)
        else:
            formater.text_item(text)
        formater.end_list()

    def copy(self):
        """The CircularArc diagram layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = CircularArc(self.get_trunk())
        self.copy_base(new_one)
        new_one.linecolor = self.linecolor.copy()
        new_one.line_width = self.line_width
        new_one.size = self.size
        new_one.start_angle = self.start_angle
        new_one.angle = self.angle
        new_one.sampler = self.sampler.copy()
        return new_one
