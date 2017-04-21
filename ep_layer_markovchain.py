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
import model_locus
import model_layer
import model_constraintpool
import model_random
import ka_factory

NUMBER_OF_STATES_CONSTRAINT = 'number_of_statesconstraint'
SAMPLERTYPE_CONSTRAINT = 'samplertypeconstraint'
STAMPTYPE_CONSTRAINT = 'stamptypeconstraint'
COLORGAMUTTYPE_CONSTRAINT = 'colorgamuttypeconstraint'

class MarkovChainLayer(model_layer.Layer):
    """Markov chain layer
    inv: self.cell_colors is not None and len(self.cell_colors) == self.states
    inv: self.probability is not None and len(self.probability) == self.states
    inv: 0 <= self.states
    inv: self.sampler is not None
    inv: self.stamp is not None
    """

    cdef = [{'bind'  : NUMBER_OF_STATES_CONSTRAINT,
             'name'  : 'Number of states',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 2, 'max': 8},
            {'bind'  : SAMPLERTYPE_CONSTRAINT,
             'name'  : 'Permitted sampler types',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('sampler').keys()},
            {'bind'  : STAMPTYPE_CONSTRAINT,
             'name'  : 'Permitted stamp types',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('stamp').keys()},
            {'bind'  : COLORGAMUTTYPE_CONSTRAINT,
             'name'  : 'Permitted color gamut',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('colorgamut').keys()},
           ]

    def __init__(self, trunk):
        """Markov chain layer constructor"""
        super(MarkovChainLayer, self).__init__(trunk)
        self.states = 0
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamut_key = colorgamut_factory.keys()[0]
        self.colorgamut = colorgamut_factory.create(colorgamut_key, self.path)
        self.cell_colors = []

        self.probability = [[1.0] * self.states
                                               for dummy in range(self.states)]
        
        sampler_factory = ka_factory.get_factory('sampler')
        sampler_key = sampler_factory.keys()[0]
        self.sampler = sampler_factory.create(sampler_key, self.path)
        
        stamp_factory = ka_factory.get_factory('stamp')
        stamp_key = stamp_factory.keys()[0]
        self.stamp = stamp_factory.create(stamp_key, self.path, self.states)

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in self.cell_colors:
            result += ka_debug.dot_ref(anchor, ref)
        for ref in self.probability:
            result += ka_debug.dot_ref(anchor, ref)
        for ref in [self.sampler, self.stamp, self.colorgamut]:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def _init_states(self, number_of_states):
        """
        pre: number_of_states >= 2
        post: self.states == number_of_states
        """
        if self.states == number_of_states:
            return False
        else:
            if self.states > number_of_states:
                self._shrink_states(number_of_states)
            elif self.states < number_of_states:
                self._append_states(number_of_states)
            self.states = number_of_states
            return True

    def _append_states(self, number_of_states):
        """
        pre: self.states < number_of_states
        pre: number_of_states > 0
        """
        for dummy in range(self.states, number_of_states):
            self.cell_colors.append(
                      self.colorgamut.get_randomized_color(self.path))
        # completely recalculate probabilities
        self.probability = [[1.0 / number_of_states] * number_of_states
                                            for dummy in range(number_of_states)]
        for row, row_probabilities in enumerate(self.probability):
            for col in range(len(row_probabilities)):
                self.probability[row][col] = random.random() / number_of_states
            self._normalize_row(row)

    def _shrink_states(self, number_of_states):
        """
        pre: self.states > number_of_states
        pre: number_of_states > 0
        """
        # copy remaining cell colors
        copy_cell_colors = [None] * number_of_states
        for cix in range(number_of_states):
            copy_cell_colors[cix] = self.cell_colors[cix].copy()
        self.cell_colors = copy_cell_colors
        # copy remaining probabilities
        copy_probability = [[1.0] * number_of_states
                                        for dummy in range(number_of_states)]
        for row, row_probabilities in enumerate(copy_probability):
            for col in range(len(row_probabilities)):
                copy_probability[row][col] = self.probability[row][col]
            self._normalize_row(row)
        self.probability = copy_probability

    def _normalize_row(self, row):
        row_probabilities = self.probability[row]
        row_sum = 0.0
        for column in range(len(row_probabilities)):
            row_sum += self.probability[row][column]
        normalize = 1.0 / row_sum
        for column in range(len(row_probabilities)):
            self.probability[row][column] *= normalize

    def __eq__(self, other):
        """Equality based on the layers components."""
        equal = isinstance(other, MarkovChainLayer) \
                and super(MarkovChainLayer, self).__eq__(other) \
                and self.states == other.states \
                and self.sampler == other.sampler \
                and self.stamp == other.stamp \
                and self.colorgamut == other.colorgamut
        if equal:
            for cix, cell_color in enumerate(self.cell_colors):
                equal = equal and cell_color == other.cell_colors[cix]
        if equal:
            for row, row_probabilities in enumerate(self.probability):
                for col, cell_probability in enumerate(row_probabilities):
                    equal = equal \
                            and cell_probability == other.probability[row][col]
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(MarkovChainLayer, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
        self.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                           self.path)
        self.colorgamut.randomize()

        number_of_states_constraint = cpool.get(self, NUMBER_OF_STATES_CONSTRAINT)
        self._init_states(model_random.randint_constrained(
                                                  number_of_states_constraint))
            
        sampler_factory = ka_factory.get_factory('sampler')
        samplertype_constraint = cpool.get(self, SAMPLERTYPE_CONSTRAINT)
        self.sampler = sampler_factory.create_random(samplertype_constraint, 
                                                     self.path)
        self.sampler.randomize()

        stamp_factory = ka_factory.get_factory('stamp')
        stamptype_constraint = cpool.get(self, STAMPTYPE_CONSTRAINT)
        self.stamp = stamp_factory.create_random(stamptype_constraint, 
                                                 self.path, self.states)
        self.stamp.randomize()

    def mutate(self):
        """Make random changes to the layers components."""
        super(MarkovChainLayer, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        number_of_states_constraint = cpool.get(self, NUMBER_OF_STATES_CONSTRAINT)
        changed = self._init_states(model_random.jitter_discret_constrained(
                                    self.states, number_of_states_constraint))

        if not changed:
            for row, row_probabilities in enumerate(self.probability):
                for col in range(len(row_probabilities)):
                    self.probability[row][col] += \
                                            model_random.jitter(1.0 / self.states)
                self._normalize_row(row)

        self.sampler.mutate()
        self.stamp.mutate()
        self.colorgamut.mutate()
        for cix in range(len(self.cell_colors)):
            self.colorgamut.adjust_color(self.cell_colors[cix])

    def swap_places(self):
        """Shuffle similar components."""
        model_random.swap_places(self.cell_colors)
        model_random.swap_places(self.probability)
        for row, row_probabilities in enumerate(self.probability):
            model_random.swap_places(row_probabilities)
            self._normalize_row(row)
        self.sampler.swap_places()
        self.stamp.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, MarkovChainLayer)
        pre: isinstance(self, MarkovChainLayer)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = MarkovChainLayer(self.get_trunk())
        cross_sequence = self.crossingover_base(new_one, other, 2)
        new_one.sampler = model_random.crossingover_elem(self.sampler,
                                                         other.sampler)
        new_one.stamp = model_random.crossingover_elem(self.stamp,
                                                       other.stamp)
        if cross_sequence[1]:
            probability = other.probability
            cell_colors = other.cell_colors
            new_one.states = other.states
        else:
            probability = self.probability
            cell_colors = self.cell_colors
            new_one.states = self.states
        new_one.probability = [[1.0 / new_one.states] * new_one.states
                                            for dummy in range(new_one.states)]
        for row, row_probabilities in enumerate(probability):
            for col, cell_probability in enumerate(row_probabilities):
                new_one.probability[row][col] = cell_probability

        new_one.colorgamut = other.colorgamut.copy() if cross_sequence[0] \
                                                     else self.colorgamut.copy() 
        new_one.cell_colors = []
        for cix in range(len(cell_colors)):
            color = cell_colors[cix].copy()
            new_one.colorgamut.adjust_color(color)
            new_one.cell_colors.append(color)
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
        cell_rand = random.Random(self.random_seed)
        cell_state = 0
        for point in self.sampler.get_sample_points():
            rgba = self.cell_colors[cell_state].rgba
            ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
            self.stamp.render(ctx, point, cell_state)
            cell_state = self._next_state(cell_state, cell_rand)

    def _next_state(self, cell_state, cell_rand):
        next_cell_state = self.states-1
        row_probabilities = self.probability[cell_state]
        cell_sum, level = 0.0, cell_rand.random()
        for column, cell_probability in enumerate(row_probabilities):
            cell_sum += cell_probability
            if cell_sum >= level:
                next_cell_state = column
                break
        return next_cell_state

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(MarkovChainLayer, self).explain(formater)
        self.colorgamut.explain(formater)
        formater.color_array(self.cell_colors, _('cell colors:'))
        formater.text_item(_('number of states: ') + str(self.states))
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
        """The Markov chain layer copy constructor
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = MarkovChainLayer(self.get_trunk())
        self.copy_base(new_one)
        new_one.states = self.states
        new_one.cell_colors = [None] * self.states
        for cix in range(len(self.cell_colors)):
            new_one.cell_colors[cix] = self.cell_colors[cix].copy()
        new_one.probability = [[0.0] * self.states
                                               for dummy in range(self.states)]
        for row, row_probabilities in enumerate(self.probability):
            for col, cell_probability in enumerate(row_probabilities):
                new_one.probability[row][col] = cell_probability
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
