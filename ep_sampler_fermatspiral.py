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
STEPS_CONSTRAINT = 'stepsconstraint'
ANGLE_CONSTRAINT = 'angleconstraint'
C_CONSTRAINT = 'cconstraint'

class FermatSpiralSampler(model_allele.Allele):
    """FermatSpiralSampler: Reverse the layer horizontally or vertically.
    """

    cdef = [{'bind'  : X_CENTER_CONSTRAINT,
             'name'  : 'Center point x',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -1.0, 'max': 2.0},
             {'bind'  : Y_CENTER_CONSTRAINT,
             'name'  : 'Center point y',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -1.0, 'max': 2.0},
             {'bind'  : STEPS_CONSTRAINT,
             'name'  : 'Number of samples.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : -50, 'max': 50},
             {'bind'  : ANGLE_CONSTRAINT,
             'name'  : 'Angle per sampling step for Fermat spiral',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -math.pi, 'max': math.pi},
             {'bind'  : C_CONSTRAINT,
             'name'  : 'Scaling constant for Fermat spiral',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -0.1, 'max': 0.1},
           ]                                                  

    def __init__(self, trunk):
        """Constructor for a flip merger."""
        super(FermatSpiralSampler, self).__init__(trunk)
        self.x_center = 0.5
        self.y_center = 0.5
        self.start = 1
        self.end = 1
        self.angle = 0.0
        self.c = 0.0

    def __eq__(self, other):
        """Equality based on fliping horizontally or vertically."""
        equal = isinstance(other, FermatSpiralSampler) \
                and self.x_center == other.x_center \
                and self.y_center == other.y_center \
                and self.start == other.start \
                and self.end == other.end \
                and self.angle == other.angle \
                and self.c == other.c
        return equal

    def randomize(self):
        """Randomize"""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        x_center_constraint = cpool.get(self, X_CENTER_CONSTRAINT)
        self.x_center = model_random.uniform_constrained(x_center_constraint)
        y_center_constraint = cpool.get(self, Y_CENTER_CONSTRAINT)
        self.y_center = model_random.uniform_constrained(y_center_constraint)
        steps_constraint = cpool.get(self, STEPS_CONSTRAINT)
        self.start = model_random.randint_constrained(steps_constraint)
        self.end = model_random.randint_constrained(steps_constraint)
        angle_constraint = cpool.get(self, ANGLE_CONSTRAINT)
        self.angle = model_random.uniform_constrained(angle_constraint)
        c_constraint = cpool.get(self, C_CONSTRAINT)
        self.c = model_random.uniform_constrained(c_constraint)

    def mutate(self):
        """Mutate"""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        x_center_constraint = cpool.get(self, X_CENTER_CONSTRAINT)
        self.x_center = model_random.jitter_constrained(self.x_center,
                                                        x_center_constraint)
        y_center_constraint = cpool.get(self, Y_CENTER_CONSTRAINT)
        self.y_center = model_random.jitter_constrained(self.y_center,
                                                        y_center_constraint)
        steps_constraint = cpool.get(self, STEPS_CONSTRAINT)
        if model_random.is_mutating():
            self.start = model_random.jitter_discret_constrained(self.start,
                                                            steps_constraint)
        if model_random.is_mutating():
            self.end = model_random.jitter_discret_constrained(self.end,
                                                            steps_constraint)
        angle_constraint = cpool.get(self, ANGLE_CONSTRAINT)
        self.angle = model_random.jitter_constrained(self.angle, angle_constraint)
        c_constraint = cpool.get(self, C_CONSTRAINT)
        self.c = model_random.jitter_constrained(self.c, c_constraint)

    def swap_places(self):
        """Exchange x- and y-center."""
        self.x_center, self.y_center = model_random.swap_parameters(self.x_center,
                                                                    self.y_center)

    def crossingover(self, other):
        """
        pre: isinstance(other, FermatSpiralSampler)
        pre: isinstance(self, FermatSpiralSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = FermatSpiralSampler(self.get_trunk())
        cross_sequence = model_random.crossing_sequence(6)
        new_one.x_center = self.x_center if cross_sequence[0] else other.x_center
        new_one.y_center = self.y_center if cross_sequence[1] else other.y_center
        new_one.start = self.start if cross_sequence[2] else other.start
        new_one.end = self.end if cross_sequence[3] else other.end
        new_one.angle = self.angle if cross_sequence[4] else other.angle
        new_one.c = self.c if cross_sequence[5] else other.c
        return new_one

    def get_sample_points(self):
        """Produces a list of sampling points.
        """
        sample_points = []
        ox, oy = self.x_center, self.y_center
        stepping = range(self.start, self.end+1) if self.start < self.end \
                                          else range(self.end, self.start-1, -1)
        for n in stepping:
            phi = n * self.angle
            r = self.c * math.sqrt(math.fabs(n))
            x = ox + r * math.cos(phi)
            y = oy + r * math.sin(phi)
            if math.fabs(x) < 1000 and math.fabs(y) < 1000:
                sample_points.append( (x, y) )
        return sample_points

    def get_sample_extent(self):
        """'Size' of one sample as a fraction of 1.
        """
        diff = self.end - self.start if self.start < self.end \
                                     else self.start - self.end
        size = 1.0 if diff == 0 else 1.0/diff
        return size, size

    def explain(self):
        """
        post: len(__return__) == 3
        """
        head = _("Fermat's spiral sampler: center=%f,%f, start steps=%d, end steps=%d, radian=%f, scaling=%f") \
                                    % (self.x_center, self.y_center,
                                       self.start, self.end, self.angle, self.c)
        return ka_utils.explain_points(head, self.get_sample_points())

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, FermatSpiralSampler)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = FermatSpiralSampler(self.get_trunk())
        new_one.x_center = self.x_center
        new_one.y_center = self.y_center
        new_one.start = self.start
        new_one.end = self.end
        new_one.angle = self.angle
        new_one.c = self.c
        return new_one
