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
This module handles a continuous red, green, blue and alpha color space."""

import random
import colorsys
import model_random
import model_locus
from gettext import gettext as _

class NoneColorConstraint(model_locus.Locus):
    """No color constraint."""

    def __init__(self, trunk):
        """Color constraint constructor."""
        super(NoneColorConstraint, self).__init__(trunk)
        
    def filter(self, rgba):
        """Use unfiltered red, green, blue and alpha  values.
        pre: len(rgba) == 4
        post: len(__return__) == 4
        """
        return (rgba[0], rgba[1], rgba[2], rgba[3])

    def randomize(self):
        """Set red, green, blue and alpha to random values.
        post: len(__return__) == 4
        """
        return (random.random(), random.random(), random.random(), \
                random.random())

    def mutate(self, rgba):
        """Make small random changes in hue, lightness, saturation.
        pre: len(rgba) == 4
        post: len(__return__) == 4
        """
        hue, lightness, saturation = colorsys.rgb_to_hls( \
                                  rgba[0], rgba[1], rgba[2])
        hue = model_random.cyclic_limit(hue + 0.1 * (random.random() - 0.5))
        lightness = model_random.limit(lightness + 0.1 * (random.random() - 0.5))
        saturation = model_random.limit(saturation + 0.1 * (random.random() - 0.5))
        alpha = model_random.limit(rgba[3] + 0.1 * (random.random() - 0.5))
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        return (rgb[0], rgb[1], rgb[2], alpha)

    def explain(self, rgba, alpha=True):
        """Explain current values.
        pre: len(rgba) == 4
        """
        if alpha:
            return _('%d%% red, %d%% green, %d%% blue, %d%% opaque') \
                         % (100*rgba[0], 100*rgba[1], 100*rgba[2], 100*rgba[3])
        else:
            return _('%d%% red, %d%% green, %d%% blue') \
                         % (100*rgba[0], 100*rgba[1], 100*rgba[2])
