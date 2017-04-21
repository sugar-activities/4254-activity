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

SIZE_CONSTRAINT = 'sizeconstraint'
STATES_CONSTRAINT = 'statesconstraint'
COLORGAMUTTYPE_CONSTRAINT = 'colorgamuttypeconstraint'
LEFT_NEIGHBORS_CONSTRAINT = 'leftneighborsconstraint'
RIGHT_NEIGHBORS_CONSTRAINT = 'rightneighborsconstraint'

class LcaLayer(model_layer.Layer):
    """LcaLayer
    inv: len(self.cell_colors) > 0
    inv: self.size >= 1
    inv: self.states >= 1
    inv: self.left_neighbors >= 0
    inv: self.right_neighbors >= 0
    """

    cdef = [{'bind'  : SIZE_CONSTRAINT,
             'name'  : 'Number of cells.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 2, 'max': 32},
            {'bind'  : STATES_CONSTRAINT,
             'name'  : 'Number of states.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 2, 'max': 6},
            {'bind'  : LEFT_NEIGHBORS_CONSTRAINT,
             'name'  : 'Number of left neighbors.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0, 'max': 2},
            {'bind'  : RIGHT_NEIGHBORS_CONSTRAINT,
             'name'  : 'Number of right neighbors.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0, 'max': 2},
            {'bind'  : COLORGAMUTTYPE_CONSTRAINT,
             'name'  : 'Permitted color gamut',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_factory.get_factory('colorgamut').keys()},
           ]

    def __init__(self, trunk):
        """linear cellular automata layer constructor
        post: len(self.cell_colors) == self.states
        """
        super(LcaLayer, self).__init__(trunk)
        self.size = 2
        self.states = 2
        self.left_neighbors = 1
        self.right_neighbors = 1
        rsize = self.states ** (self.left_neighbors + 1 + self.right_neighbors)
        self.rules = [0 for dummy in xrange(rsize)]
        self.sequence_ordering = 0.25

        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamut_key = colorgamut_factory.keys()[0]
        self.colorgamut = colorgamut_factory.create(colorgamut_key, self.path)
        self.cell_colors = [self.colorgamut.get_randomized_color(self.path),
                            self.colorgamut.get_randomized_color(self.path), ]

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.colorgamut, ]:
            result += ka_debug.dot_ref(anchor, ref)
        for ref in self.cell_colors:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality """
        equal = isinstance(other, LcaLayer) \
                and model_layer.Layer.__eq__(self, other) \
                and self.size == other.size \
                and self.states == other.states \
                and self.left_neighbors == other.left_neighbors \
                and self.right_neighbors == other.right_neighbors \
                and self.sequence_ordering == other.sequence_ordering \
                and len(self.cell_colors) == len(other.cell_colors)
        if equal:
            for index, rule in enumerate(self.rules):
                equal = equal and rule == other.rules[index]
        if equal:
            for index, site_color in enumerate(self.cell_colors):
                equal = equal and site_color == other.cell_colors[index]
        return equal

    def randomize(self):
        """Randomize the layers components.
        post: len(self.cell_colors) == self.states
        post: forall(self.rules, lambda f: 0 <= f < self.states)
        """
        super(LcaLayer, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        size_constraint = cpool.get(self, SIZE_CONSTRAINT)
        self.size = model_random.randint_constrained(size_constraint)
        
        states_constraint = cpool.get(self, STATES_CONSTRAINT)
        self.states = model_random.randint_constrained(states_constraint)
        
        left_neighbors_constraint = cpool.get(self, LEFT_NEIGHBORS_CONSTRAINT)
        self.left_neighbors = model_random.randint_constrained(left_neighbors_constraint)
        right_neighbors_constraint = cpool.get(self, RIGHT_NEIGHBORS_CONSTRAINT)
        self.right_neighbors = model_random.randint_constrained(right_neighbors_constraint)
        
        self.rules = [random.randrange(0, self.states) \
                                for dummy in xrange(self.get_numberof_rules())]
        self.sequence_ordering = random.uniform(0.0, 1.0)
        
        colorgamut_factory = ka_factory.get_factory('colorgamut')
        colorgamuttype_constraint = cpool.get(self, COLORGAMUTTYPE_CONSTRAINT)
        self.colorgamut = colorgamut_factory.create_random(colorgamuttype_constraint, 
                                                           self.path)
        self.colorgamut.randomize()

        self.cell_colors = []
        for dummy in range(self.states):
            site_color = self.colorgamut.get_randomized_color(self.path)
            self.cell_colors.append(site_color)

    def fill_sequence(self, lca_state):
        """
        post: forall(lca_state, lambda f: 0 <= f < self.states)
        """
        seq_random = random.Random()
        seq_random.seed(self.random_seed)
        state = lca_state[0] = seq_random.randrange(0, self.states)
        for index in xrange(1, len(lca_state)):
            if seq_random.uniform(0.0, 1.0) < self.sequence_ordering:
                state = seq_random.randrange(0, self.states)
            lca_state[index] = state


    def patch_rulesize(self):
        rsize = self.get_numberof_rules()
        if len(self.rules) > rsize:
            self.rules = self.rules[:rsize]
        while len(self.rules) < rsize:
            self.rules.append(random.randrange(0, self.states))
        
        self.rules = [x % self.states for x in self.rules]


    def patch_colorsize(self):
        if len(self.cell_colors) > self.states:
            self.cell_colors = self.cell_colors[:self.states]
        while len(self.cell_colors) < self.states:
            site_color = self.colorgamut.get_randomized_color(self.path)
            self.cell_colors.append(site_color)

    def mutate(self):
        """Make small random changes to the layers components.
        post: len(self.cell_colors) == self.states
        post: forall(self.rules, lambda f: 0 <= f < self.states)
        """
        super(LcaLayer, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        size_constraint = cpool.get(self, SIZE_CONSTRAINT)
        self.size = model_random.jitter_discret_constrained(
                                                  self.size, size_constraint)
        states_constraint = cpool.get(self, STATES_CONSTRAINT)
        self.states = model_random.jitter_discret_constrained(
                                                  self.states, states_constraint)

        left_neighbors_constraint = cpool.get(self, LEFT_NEIGHBORS_CONSTRAINT)
        self.left_neighbors = model_random.randint_constrained(left_neighbors_constraint)
        self.left_neighbors = model_random.jitter_discret_constrained(
                                 self.left_neighbors, left_neighbors_constraint)
        right_neighbors_constraint = cpool.get(self, RIGHT_NEIGHBORS_CONSTRAINT)
        self.right_neighbors = model_random.jitter_discret_constrained(
                               self.right_neighbors, right_neighbors_constraint)
        self.patch_rulesize()

        self.patch_colorsize()
        self.colorgamut.mutate()
        for cix in range(len(self.cell_colors)):
            self.colorgamut.adjust_color(self.cell_colors[cix])

    def swap_places(self):
        """Shuffle similar components."""
        model_random.swap_places(self.cell_colors)
        model_random.swap_places(self.rules)

    def crossingover(self, other):
        """
        pre: isinstance(other, LcaLayer)
        pre: isinstance(self, LcaLayer)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        post: len(__return__.cell_colors) == __return__.states
        post: len(__return__.rules) == __return__.get_numberof_rules()
        post: forall(__return__.rules, lambda f: 0 <= f < __return__.states)
        """
        new_one = LcaLayer(self.get_trunk())
        cross_sequence = self.crossingover_base(new_one, other, 6)
        new_one.size = self.size if cross_sequence[0] \
                                 else other.size
        new_one.states = self.states if cross_sequence[1] \
                                     else other.states
        #TODO rules an die geänderten states anpassen.
        
        new_one.left_neighbors = self.left_neighbors if cross_sequence[2] \
                                                     else other.left_neighbors
        new_one.right_neighbors = self.right_neighbors if cross_sequence[3] \
                                                       else other.right_neighbors
        new_one.colorgamut = other.colorgamut.copy() if cross_sequence[4] \
                                                     else self.colorgamut.copy() 
        new_one.sequence_ordering = self.sequence_ordering if cross_sequence[5] \
                                                           else other.sequence_ordering

        new_one.rules = model_random.crossingover_nativeelement_list(self.rules, \
                                                                     other.rules)
        new_one.patch_rulesize()

        new_one.cell_colors = model_random.crossingover_list(self.cell_colors,
                                                             other.cell_colors)
        new_one.patch_colorsize()
        for cix in range(len(new_one.cell_colors)):
            new_one.colorgamut.adjust_color(new_one.cell_colors[cix])

        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        self.begin_render(ctx, width, height)
        lca_state = [0 for dummy in xrange(self.size)]
        lca_nextstate = [0 for dummy in xrange(self.size)]
        self.fill_sequence(lca_state)
        delta = 1.0 / self.size
        next_state = 0
        x_pos = -0.5
        for dummy in xrange(self.size):
            y_pos = -0.5
            for col in xrange(self.size):
                ruleNumber = self.get_rule_index(lca_state, col)
                next_state = lca_nextstate[col] = self.rules[ruleNumber]
                rgba = self.cell_colors[next_state % len(self.cell_colors)].rgba
                ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
                ctx.rectangle(x_pos, y_pos, delta, delta)
                ctx.fill()
                y_pos += delta
            x_pos += delta
            # copy temporary cell array to actual cell array
            lca_state = lca_nextstate[:]

    def get_numberof_rules(self):
        """
        post: __return__ >= 1
        """
        return self.states ** (self.left_neighbors + 1 + self.right_neighbors)
  
    def get_rule_index(self, lca_state, index):
        """
        pre: len(lca_state) == self.size
        pre: 0 <= index < self.size
        post: 0 <= __return__ < len(self.rules)
        """
        ruleNumber = 0
        for nx in xrange(index - self.left_neighbors,
                         index + self.right_neighbors + 1):
            ruleNumber *= self.states
            ruleNumber += lca_state[nx % len(lca_state)]
        return ruleNumber

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(LcaLayer, self).explain(formater)
        formater.text_item(_('Number of states: ') + str(self.states))
        formater.text_item(_('Number of left neighbors: ') + str(self.left_neighbors))
        formater.text_item(_('Number of right neighbors: ') + str(self.right_neighbors))
        formater.text_item(_('Number of cells: ') + str(self.size))
        formater.text_item(_('Stability of sequence ordering: ') + str(self.size))
        self.colorgamut.explain(formater)
        formater.color_array(self.cell_colors, _('Cell colors:'))
        formater.end_list()

    def copy(self):
        """The linear cellular automata layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        pre: len(self.cell_colors) == self.states
        post: len(__return__.cell_colors) == __return__.states
        """
        new_one = LcaLayer(self.get_trunk())
        self.copy_base(new_one)
        new_one.cell_colors = model_random.copy_list(self.cell_colors)
        new_one.states = self.states
        new_one.rules = self.rules[:]
        new_one.size = self.size
        new_one.left_neighbors = self.left_neighbors
        new_one.right_neighbors = self.right_neighbors
        new_one.sequence_ordering = self.sequence_ordering
        new_one.colorgamut = self.colorgamut.copy()
        return new_one
