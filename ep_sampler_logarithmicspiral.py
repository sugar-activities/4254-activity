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

import ka_utils
import model_random
import model_locus
import model_allele
import model_constraintpool
from gettext import gettext as _
import math

X_CENTER_CONSTRAINT = 'xcenterconstraint'
Y_CENTER_CONSTRAINT = 'ycenterconstraint'
TURNS_CONSTRAINT = 'turnsconstraint'
STEPS_CONSTRAINT = 'stepsconstraint'
A_CONSTRAINT = 'aconstraint'
B_CONSTRAINT = 'bconstraint'

class LogarithmicSpiralSampler(model_allele.Allele):
    """LogarithmicSpiralSampler: Reverse the layer horizontally or vertically.
    inv: self.a >= 0.0
    inv: self.b >= 0.0
    inv: self.steps >= 1
    """

    cdef = [{'bind'  : X_CENTER_CONSTRAINT,
             'name'  : 'Center point x',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -1.0, 'max': 2.0},
             {'bind'  : Y_CENTER_CONSTRAINT,
             'name'  : 'Center point y',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -1.0, 'max': 2.0},
             {'bind'  : TURNS_CONSTRAINT,
             'name'  : 'Revolution of logarithmic spiral',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -10.0, 'max': 10.0},
             {'bind'  : STEPS_CONSTRAINT,
             'name'  : 'Number of samples per revolution.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 3, 'max': 36},
             {'bind'  : A_CONSTRAINT,
             'name'  : 'Scaling constant for logarithmic spiral',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.0, 'max': 1.0},
             {'bind'  : B_CONSTRAINT,
             'name'  : 'Scaling constant for logarithmic spiral',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.0, 'max': 1.0},
           ]                                                  

    def __init__(self, trunk):
        """Constructor for a flip merger."""
        super(LogarithmicSpiralSampler, self).__init__(trunk)
        self.x_center = 0.5
        self.y_center = 0.5
        self.steps = 1
        self.turns = 1.0
        self.a = 1.0
        self.b = 1.0

    def __eq__(self, other):
        """Equality based on fliping horizontally or vertically."""
        equal = isinstance(other, LogarithmicSpiralSampler) \
                and self.x_center == other.x_center \
                and self.y_center == other.y_center \
                and self.steps == other.steps \
                and self.turns == other.turns \
                and self.a == other.a \
                and self.b == other.b
        return equal

    def randomize(self):
        """Randomize"""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        x_center_constraint = cpool.get(self, X_CENTER_CONSTRAINT)
        self.x_center = model_random.uniform_constrained(x_center_constraint)
        y_center_constraint = cpool.get(self, Y_CENTER_CONSTRAINT)
        self.y_center = model_random.uniform_constrained(y_center_constraint)
        steps_constraint = cpool.get(self, STEPS_CONSTRAINT)
        self.steps = model_random.randint_constrained(steps_constraint)
        turns_constraint = cpool.get(self, TURNS_CONSTRAINT)
        self.turns = model_random.uniform_constrained(turns_constraint)
        a_constraint = cpool.get(self, A_CONSTRAINT)
        self.a = model_random.uniform_constrained(a_constraint)
        b_constraint = cpool.get(self, B_CONSTRAINT)
        self.b = model_random.uniform_constrained(b_constraint)

    def mutate(self):
        """Mutate"""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        x_center_constraint = cpool.get(self, X_CENTER_CONSTRAINT)
        self.x_center = model_random.jitter_constrained(self.x_center,
                                                        x_center_constraint)
        y_center_constraint = cpool.get(self, Y_CENTER_CONSTRAINT)
        self.y_center = model_random.jitter_constrained(self.y_center,
                                                        y_center_constraint)
        if model_random.is_mutating():
            steps_constraint = cpool.get(self, STEPS_CONSTRAINT)
            self.steps = model_random.jitter_discret_constrained(self.steps,
                                                            steps_constraint)
        turns_constraint = cpool.get(self, TURNS_CONSTRAINT)
        self.turns = model_random.jitter_constrained(self.turns,
                                                        turns_constraint)
        a_constraint = cpool.get(self, A_CONSTRAINT)
        self.a = model_random.jitter_constrained(self.a, a_constraint)
        b_constraint = cpool.get(self, B_CONSTRAINT)
        self.b = model_random.jitter_constrained(self.b, b_constraint)

    def swap_places(self):
        """Exchange x- and y-center."""
        self.x_center, self.y_center = model_random.swap_parameters(self.x_center,
                                                                    self.y_center)

    def crossingover(self, other):
        """
        pre: isinstance(other, LogarithmicSpiralSampler)
        pre: isinstance(self, LogarithmicSpiralSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = LogarithmicSpiralSampler(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(6)
        new_one.x_center = self.x_center if cross_sequence[0] else other.x_center
        new_one.y_center = self.y_center if cross_sequence[1] else other.y_center
        new_one.steps = self.steps if cross_sequence[2] else other.steps
        new_one.turns = self.turns if cross_sequence[3] else other.turns
        new_one.a = self.a if cross_sequence[4] else other.a
        new_one.b = self.b if cross_sequence[5] else other.b
        return new_one

    def get_sample_points(self):
        """ Produces a list of sampling points.
        """
        sample_points = []
        ox, oy = self.x_center, self.y_center
        angularStep = (2 * math.pi) / self.steps
        turns = self.turns
        ccw = 1
        if turns < 0:
            turns = -turns
            ccw = -1
        for n in range(int(turns * self.steps)):
            phi = n * angularStep
            a2, b2  = self.a**2, self.b**2
            r = a2 * math.exp(b2 * phi)
            x = ox + r * math.cos(ccw * phi)
            y = oy + r * math.sin(ccw * phi)
            if math.fabs(x) < 1000 and math.fabs(y) < 1000:
                sample_points.append( (x, y) )
        return sample_points

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        size = 1.0/self.steps
        return size, size

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _('Logarithmic spiral sampler: center=%f,%f, revolutions=%f, steps per revolution=%d, a=%f, b=%f') \
                                    % (self.x_center, self.y_center,
                                       self.turns, self.steps, self.a, self.b)
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, LogarithmicSpiralSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = LogarithmicSpiralSampler(self.get_trunk())
        new_one.x_center = self.x_center
        new_one.y_center = self.y_center
        new_one.steps = self.steps
        new_one.turns = self.turns
        new_one.a = self.a
        new_one.b = self.b
        return new_one
