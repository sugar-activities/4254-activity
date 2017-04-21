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
import colorsys
import model_random
import model_locus
import exon_color
from gettext import gettext as _

class AnalogousColorGamut(model_locus.Locus):
    """Manages a series of similar colors."""

    def __init__(self, trunk):
        """Color gamut constructor."""
        super(AnalogousColorGamut, self).__init__(trunk)
        self.hue = 0.0
        self.range = 0.1
        
    def __eq__(self, other):
        """Equality based on the gamuts components."""
        equal = isinstance(other, AnalogousColorGamut) \
                and self.hue == other.hue \
                and self.range == other.range
        return equal

    def randomize(self):
        """Set hue.
        """
        self.hue = random.random()
        self.range = (60.0 / 360.0) * random.random()

    def get_randomized_color(self, path):
        """Set red, green, blue and alpha to random values.
        """
        deviate = self.range * (random.random() - 0.5)
        hue = model_random.cyclic_limit(self.hue + deviate)
        lightness = random.random()
        saturation = random.random()
        alpha = random.random()
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        color = exon_color.Color(path, rgb[0], rgb[1], rgb[2], alpha)
        color.set_base_color(deviate, 0.0, 0.0)
        return color

    def mutate(self):
        """Make small random changes in hue.
        """
        self.hue = model_random.cyclic_limit(self.hue + model_random.jitter(0.1))
        self.range += model_random.jitter(0.1)

    def adjust_color(self, color):
        """Adjust rgba value to mutated hue and similarity range.
        pre: len(color.rgba) == 4
        """
        rgba = color.rgba
        dummy, lightness, saturation = colorsys.rgb_to_hls(
                                  rgba[0], rgba[1], rgba[2])
        deviate = color.base_diff_hue 
        rgb = colorsys.hls_to_rgb(self.hue + deviate, lightness, saturation)
        color.rgba = (rgb[0], rgb[1], rgb[2], rgba[3])

    def explain(self, formater):
        formater.text_item(_('Analogous color scheme'))

    def copy(self):
        """The AnalogousColorGamut copy constructor
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = AnalogousColorGamut(self.get_trunk())
        new_one.hue = self.hue
        new_one.range = self.range
#        new_one.angle = {}
#        for key, value in self.angle.items():
#            new_one.angle[key] = value
        return new_one
