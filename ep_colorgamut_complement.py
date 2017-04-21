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

class ComplementaryColorGamut(model_locus.Locus):
    """Manages a series of complementary colors."""

    def __init__(self, trunk):
        """Color gamut constructor."""
        super(ComplementaryColorGamut, self).__init__(trunk)
        self.hue = 0.0
        
    def __eq__(self, other):
        """Equality based on the gamuts components."""
        equal = isinstance(other, ComplementaryColorGamut) \
                and self.hue == other.hue
        return equal

    def randomize(self):
        """Set hue.
        """
        self.hue = random.random()

    def get_randomized_color(self, path):
        """Set red, green, blue and alpha to random values.
        """
        lightness = random.random()
        saturation = random.random()
        alpha = random.random()
        deviate = 0.0 if random.randint(0,1) == 0 else 0.5
        rgb = colorsys.hls_to_rgb(self.hue+deviate, lightness, saturation)
        color = exon_color.Color(path, rgb[0], rgb[1], rgb[2], alpha)
        color.set_base_color(deviate, 0.0, 0.0)
        return color

    def mutate(self):
        """Make small random changes in hue.
        """
        self.hue = model_random.cyclic_limit(self.hue + model_random.jitter(0.1))

    def adjust_color(self, color):
        """Adjust rgba value to mutated hue.
        pre: len(color.rgba) == 4
        """
        rgba = color.rgba
        dummy, lightness, saturation = colorsys.rgb_to_hls( \
                                  rgba[0], rgba[1], rgba[2])
        deviate = color.base_diff_hue 
        rgb = colorsys.hls_to_rgb(self.hue+deviate, lightness, saturation)
        color.rgba = (rgb[0], rgb[1], rgb[2], rgba[3])

    def explain(self, formater):
        formater.text_item(_('Complementary color scheme'))

    def copy(self):
        """The ComplementaryColorGamut copy constructor
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = ComplementaryColorGamut(self.get_trunk())
        new_one.hue = self.hue
        return new_one
