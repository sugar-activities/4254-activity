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

import ka_debug
import model_random
import ka_factory
import model_locus
import model_layer
import model_constraintpool
import exon_position

ORDER_CONSTRAINT = 'order_constaint'
SAMPLERTYPE_CONSTRAINT = 'samplertypeconstraint'
STAMPTYPE_CONSTRAINT = 'stamptypeconstraint'
NUMBER_OF_SITES_CONSTRAINT = 'sitenumberofconstraint'
COLORGAMUTTYPE_CONSTRAINT = 'colorgamuttypeconstraint'

class VoronoiDiagramLayer(model_layer.Layer):
    """VoronoiDiagramLayer
    inv: len(self.sites_point) > 0
    inv: len(self.sites_color) > 0
    inv: self.sampler is not None
    inv: self.stamp is not None
    """

    cdef = [{'bind'  : ORDER_CONSTRAINT,
             'name'  : 'Natural logarithm of order p used in Minkowski distance',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -4.0, 'max': 4.0},
            {'bind'  : NUMBER_OF_SITES_CONSTRAINT,
             'name'  : 'Number of site points',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 2, 'max': 10},
            {'bind'  : SAMPLERTYPE_CONSTRAINT,
             'name'  : 'Permitted sampler types',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_factory.get_factory('sampler').keys()},
            {'bind'  : STAMPTYPE_CONSTRAINT,
             'name'  : 'Permitted stamp types',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_factory.get_factory('stamp').keys()},
            {'bind'  : COLORGAMUTTYPE_CONSTRAINT,
             'name'  : 'Permitted color gamut',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('colorgamut').keys()},
           ]

    def __init__(self, trunk):
        """Voronoi diagram layer constructor"""
        super(VoronoiDiagramLayer, self).__init__(trunk)
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamut_key = colorgamut_factory.keys()[0]
        self.colorgamut = colorgamut_factory.create(colorgamut_key, self.path)

        self.sites_point = [exon_position.Position(self.path, 0.0, 0.0)]
        self.sites_color = [self.colorgamut.get_randomized_color(self.path)]
#        self._distance = VoronoiDiagramLayer._euclidean_square_distance
        self.order = 2 # euclidean distance
        sampler_factory = ka_factory.get_factory('sampler')
        sampler_key = sampler_factory.keys()[0]
        self.sampler = sampler_factory.create(sampler_key, self.path)
        stamp_factory = ka_factory.get_factory('stamp')
        stamp_key = stamp_factory.keys()[0]
        self.stamp = stamp_factory.create(stamp_key, self.path, len(self.sites_point))

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.sites_point:
            result += ka_debug.dot_ref(anchor, ref)
        for ref in self.sites_color:
            result += ka_debug.dot_ref(anchor, ref)
        for ref in [self.sampler, self.stamp]:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality """
        equal = isinstance(other, VoronoiDiagramLayer) \
                and model_layer.Layer.__eq__(self, other) \
                and len(self.sites_point) == len(other.sites_point) \
                and len(self.sites_color) == len(other.sites_color) \
                and self.order == other.order \
                and self.sampler == other.sampler \
                and self.stamp == other.stamp
        if equal:
            for index, site_point in enumerate(self.sites_point):
                equal = equal and site_point == other.sites_point[index]
        if equal:
            for index, site_color in enumerate(self.sites_color):
                equal = equal and site_color == other.sites_color[index]
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(VoronoiDiagramLayer, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        number_of_constraint = cpool.get(self, NUMBER_OF_SITES_CONSTRAINT)
        
        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.uniform_constrained(order_constraint)
        
        sampler_factory = ka_factory.get_factory('sampler')
        samplertype_constraint = cpool.get(self, SAMPLERTYPE_CONSTRAINT)
        self.sampler = sampler_factory.create_random(samplertype_constraint, 
                                                     self.path)
        self.sampler.randomize()

        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
        self.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                           self.path)
        self.colorgamut.randomize()

        self.sites_point = []
        for dummy in range(model_random.randint_constrained(number_of_constraint)):
            site_point = exon_position.Position(self.path, 0.0, 0.0)
            site_point.randomize()
            self.sites_point.append(site_point)
        self.sites_color = []
        for dummy in range(model_random.randint_constrained(number_of_constraint)):
            site_color = self.colorgamut.get_randomized_color(self.path)
            self.sites_color.append(site_color)

        stamp_factory = ka_factory.get_factory('stamp')
        stamptype_constraint = cpool.get(self, STAMPTYPE_CONSTRAINT)
        self.stamp = stamp_factory.create_random(stamptype_constraint, 
                                              self.path, len(self.sites_point))
        self.stamp.randomize()

    def mutate(self):
        """Make small random changes to the layers components."""
        super(VoronoiDiagramLayer, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        number_of_constraint = cpool.get(self, NUMBER_OF_SITES_CONSTRAINT)
        new_site_point = exon_position.Position(self.path, 0.0, 0.0)
        new_site_point.randomize()
        model_random.mutate_list(self.sites_point,
                                 number_of_constraint, new_site_point)

        self.colorgamut.mutate()
        new_site_color = self.colorgamut.get_randomized_color(self.path)
        model_random.mutate_list(self.sites_color,
                                 number_of_constraint, new_site_color)
        for cix in range(len(self.sites_color)):
            self.colorgamut.adjust_color(self.sites_color[cix])

        order_constraint = cpool.get(self, ORDER_CONSTRAINT)
        self.order = model_random.jitter_constrained(self.order, order_constraint)

        self.sampler.mutate()
        self.stamp.mutate()

    def swap_places(self):
        """Shuffle similar components."""
        model_random.swap_places(self.sites_point)
        model_random.swap_places(self.sites_color)
        self.sampler.swap_places()
        self.stamp.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, VoronoiDiagramLayer)
        pre: isinstance(self, VoronoiDiagramLayer)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = VoronoiDiagramLayer(self.get_trunk())
        cross_sequence = self.crossingover_base(new_one, other, 2)
        new_one.sites_point = model_random.crossingover_list(self.sites_point,
                                                             other.sites_point)

        new_one.colorgamut = other.colorgamut.copy() if cross_sequence[0] \
                                                     else self.colorgamut.copy() 
        new_one.sites_color = model_random.crossingover_list(self.sites_color,
                                                             other.sites_color)
        for cix in range(len(new_one.sites_color)):
            new_one.colorgamut.adjust_color(new_one.sites_color[cix])

        new_one.order = self.order if cross_sequence[1] else other.order
        new_one.sampler = model_random.crossingover_elem(self.sampler,
                                                         other.sampler)
        new_one.stamp = model_random.crossingover_elem(self.stamp,
                                                       other.stamp)
        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        self.begin_render(ctx, width, height)
        dw, dh = self.sampler.get_sample_extent()
        self.stamp.set_stamp_extent(dw, dh)
        for point in self.sampler.get_sample_points():
            at_index, color = self._site_color_min_dist(point)
            rgba = color.rgba
            ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
            self.stamp.render(ctx, point, at_index)

    def _site_color_min_dist(self, point):
        """ Minkowski distance
        see http://en.wikipedia.org/wiki/Minkowski_distance
        pre: len(point) == 2
        """
        
        min_distance, at_index = 999999.9, 0
        for index, site_point in enumerate(self.sites_point):
#            distance = self._distance(point, site[0])
            p = math.exp(self.order)
            try:
                distance = (math.fabs(point[0]-site_point.x_pos)**p + 
                            math.fabs(point[1]-site_point.y_pos)**p) ** (1.0/p)
                if(distance < min_distance):
                    min_distance, at_index = distance, index
            except OverflowError:
#                import sys
#                print OverflowError, sys.exc_info()[0], \
#                      '_site_color_min_dist', self.order, p, \
#                      point[0], site_point.x_pos, point[1], site_point.y_pos
                pass
        return at_index, self.sites_color[at_index % len(self.sites_color)]

#    @staticmethod
#    def _euclidean_square_distance(point, site):
#        """
#        Like Euclidean distance distance but with square root.
#        see http://en.wikipedia.org/wiki/Euclidean_distance
#        x-coordinate is stored at index [0].
#        y-coordinate is stored at index [1].
#        """
#        return (point[0]-site.x_pos)**2 + (point[1]-site.y_pos)**2
#
#    @staticmethod
#    def _manhattan_distance(point, site):
#        """ Taxicab distance, Manhattan distance)
#        see http://en.wikipedia.org/wiki/Manhattan_distance
#        x-coordinate is stored at index [0].
#        y-coordinate is stored at index [1].
#        """
#        return math.fabs(point[0]-site.x_pos) + math.fabs(point[1]-site.y_pos)
#
#    @staticmethod
#    def _chebyshev_distance(point, site):
#        """ Chebyshev distance
#        see http://en.wikipedia.org/wiki/Chebyshev_distance
#        x-coordinate is stored at index [0].
#        y-coordinate is stored at index [1].
#        """
#        dx, dy = math.fabs(point[0]-site.x_pos), math.fabs(point[1]-site.y_pos)
#        return dx if dx > dy else dy

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(VoronoiDiagramLayer, self).explain(formater)
        self.colorgamut.explain(formater)
        formater.text_item(_('Natural logarithm of order p used in Minkowski distance: ')
                           + str(self.order))
        formater.position_array(self.sites_point, _('center points for sites:'))
        self.colorgamut.explain(formater)
        formater.color_array(self.sites_color, _('site colors:'))
        text, surface, descr = self.sampler.explain()
        if surface is not None:
            formater.surface_item(surface, _('sampling points: ') + text, descr)
        else:
            formater.text_item(text)
        text, surface, descr = self.stamp.explain()
        if surface is not None:
            formater.surface_item(surface, _('stamp: ') + text, descr)
        else:
            formater.text_item(text)
        formater.end_list()

    def copy(self):
        """The Voronoi diagram layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = VoronoiDiagramLayer(self.get_trunk())
        self.copy_base(new_one)
        new_one.sites_point = model_random.copy_list(self.sites_point)
        new_one.sites_color = model_random.copy_list(self.sites_color)
        new_one.order = self.order
        new_one.sampler = self.sampler.copy()
        new_one.stamp = self.stamp.copy()
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
