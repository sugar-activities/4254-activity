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

"""Extension point for color constraints.
This module handles the black and white schema."""

import random
import model_locus
from gettext import gettext as _

EPSILON = 0.00001

class BwColorConstraint(model_locus.Locus):
    """black and white color constraint."""

    def __init__(self, trunk):
        """Color constraint constructor."""
        super(BwColorConstraint, self).__init__(trunk)
        
    def filter(self, rgba):
        """Set constraint to red, green, blue and alpha values.
        pre: len(rgba) == 4
        post: len(__return__) == 4
        """
        gray = round((rgba[0] + rgba[1] + rgba[2]) / 3.0)
        alpha = round(rgba[3])
        return (gray, gray, gray, alpha)

    def randomize(self):
        """Make a random choice between black or white.
        And make a random choice between opaque or transparent.
        post: len(__return__) == 4
        post: __return__[0]  == 0 or __return__[0] == 1
        post: __return__[3]  == 0 or __return__[3] == 1
        """
        gray = 1.0*random.randint(0, 1)
        alpha = 1.0*random.randint(0, 1)
        return (gray, gray, gray, alpha)

    def mutate(self, dummy):
        """see: randomize()
        post: len(__return__) == 4
        """
        return self.randomize()

    def explain(self, rgba, alpha=True):
        """Explain current values.
        pre: len(rgba) == 4
        """
        part1 = _('black') if abs(rgba[0]) < EPSILON else _('white')
        part2 = _(', %d%% opaque') % (100*rgba[3]) if alpha else ''
        return _('Color is reduced to black and white, ') + part1 + part2
