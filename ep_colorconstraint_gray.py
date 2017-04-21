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
from gettext import gettext as _

class GrayColorConstraint(model_locus.Locus):
    """GrayColorConstraint
    """

    def __init__(self, trunk):
        """Color constraint constructor
        """
        super(GrayColorConstraint, self).__init__(trunk)
        
    def filter(self, rgba):
        """Set constraint to red, green, blue and alpha values.
        post: len(__return__) == 4
        """
        gray = (rgba[0] + rgba[1] + rgba[2]) / 3.0
        alpha = rgba[3]
        return (gray, gray, gray, alpha)

    def randomize(self):
        """Set lightness and alpha to random values.
        post: len(__return__) == 4
        """
        gray = random.random()
        return (gray, gray, gray, random.random())

    def mutate(self, rgba):
        """Make small random changes in hue, lightness, saturation.
        post: len(__return__) == 4
        """
        gray = (rgba[0] + rgba[1] + rgba[2]) / 3.0
        gray = model_random.limit(gray + 0.1 * (random.random() - 0.5))
        alpha = model_random.limit(rgba[3] + 0.1 * (random.random() - 0.5))
        return (gray, gray, gray, alpha)

    def explain(self, rgba, alpha=True):
        """
        pre: len(rgba) == 4
        """
        if alpha:
            return _('%d%% gray, %d%% opaque') % (100*rgba[0], 100*rgba[3])
        else:
            return _('Color is reduced to shades of gray, %d%% gray') % (100*rgba[0])
