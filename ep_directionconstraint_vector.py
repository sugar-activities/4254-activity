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

"""Extension point for directional constraints.
This module handles vectors constrained by angle and length."""

import math
import model_random
import model_constraintpool
import model_locus

DISTANCE_CONSTRAINT = 'distance'
RADIAN_CONSTRAINT = 'radian'

class VectorDirectionConstraint(model_locus.Locus):
    """Constraint for direction vectors."""

    cdef = [{'bind'  : DISTANCE_CONSTRAINT,
             'name'  : 'Distance per hop',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : 0.0, 'max': 0.5,
            },
            {'bind'  : RADIAN_CONSTRAINT,
             'name'  : 'Rotation in radians',
             'domain': model_constraintpool.FLOAT_RANGE,
             'min'   : -1.0*math.pi, 'max': math.pi,
            },
           ]

    def __init__(self, trunk):
        """Direction constraint constructor."""
        super(VectorDirectionConstraint, self).__init__(trunk)
        
    def filter(self, radian, distance):
        """No constraints for radian and distance.
        post: (-1.0*math.pi) <= __return__[0] <= math.pi
        post: __return__[1] >= 0.0
        """
        return model_random.radian_limit(radian), math.fabs(distance)

    def randomize(self):
        """Set radian and distance to random values.
        post: (-1.0*math.pi) <= __return__[0] <= math.pi
        post: __return__[1] >= 0.0
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()
        radian_constraint = cpool.get(self, RADIAN_CONSTRAINT)
        distance_constraint = cpool.get(self, DISTANCE_CONSTRAINT)
        radian = model_random.uniform_constrained(radian_constraint)
        distance = model_random.uniform_constrained(distance_constraint)
        return model_random.radian_limit(radian), math.fabs(distance)

    def mutate(self, radian, distance):
        """Make small random changes in radian and distance.
        post: (-1.0*math.pi) <= __return__[0] <= math.pi
        post: __return__[1] >= 0.0
        """
        cpool = model_constraintpool.ConstraintPool.get_pool()
        radian_constraint = cpool.get(self, RADIAN_CONSTRAINT)
        distance_constraint = cpool.get(self, DISTANCE_CONSTRAINT)
        radian = model_random.jitter_constrained(radian, radian_constraint)
        distance = model_random.jitter_constrained(distance, distance_constraint)
        return model_random.radian_limit(radian), math.fabs(distance)
