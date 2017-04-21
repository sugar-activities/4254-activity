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

import random
import model_random
import model_locus

class CenteredPositionConstraint(model_locus.Locus):
    """CenteredPositionConstraint
    """

    def __init__(self, trunk):
        """Position constraint constructor
        """
        super(CenteredPositionConstraint, self).__init__(trunk)
        
    def filter(self, x_pos, y_pos):
        """Set constraint x- and y-position.
        post: len(__return__) == 2
        """
        xp = (x_pos + 0.5) / 2.0
        yp = (y_pos + 0.5) / 2.0
        return xp, yp

    def randomize(self):
        """Set x- and y-position to random values.
        post: len(__return__) == 2
        """
        return random.gauss(0.5, 0.1), random.gauss(0.5, 0.1)

    def mutate(self, x_pos, y_pos):
        """Make small random changes in x- and y-position.
        post: len(__return__) == 2
        """
        xp = x_pos + model_random.jitter(0.2)
        xp = (2.0*xp + random.gauss(0.5, 0.1)) / 3.0
        yp = y_pos + model_random.jitter(0.2)
        yp = (2.0*yp + random.gauss(0.5, 0.1)) / 3.0
        return xp, yp
