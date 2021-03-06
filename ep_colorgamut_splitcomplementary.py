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

class SplitComplementaryColorGamut(model_locus.Locus):
    """Manages split complementary colors."""

    def __init__(self, trunk):
        """Color gamut constructor."""
        super(SplitComplementaryColorGamut, self).__init__(trunk)
        self.hue = 0.0
        self.hue_deviate = (30.0 / 360.0)
        
    def __eq__(self, other):
        """Equality based on the gamuts components."""
        equal = isinstance(other, SplitComplementaryColorGamut) \
                and self.hue == other.hue \
                and self.hue_deviate == other.hue_deviate
        return equal

    def randomize(self):
        """Set hue.
        """
        self.hue = random.random()
        self.hue_deviate = (45.0 / 360.0) * random.random()

    def get_randomized_color(self, path):
        """Set red, green, blue and alpha to random values.
        """
        hue_dircetion = random.choice([-1, 0, 1])
        hue = self._get_hue(hue_dircetion)
        lightness = random.random()
        saturation = random.random()
        alpha = random.random()
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        color = exon_color.Color(path, rgb[0], rgb[1], rgb[2], alpha)
        color.set_base_color(hue_dircetion, 0, 0)
        return color

    def mutate(self):
        """Make small random changes in hue.
        """
        self.hue = model_random.cyclic_limit(self.hue + model_random.jitter(0.1))
        self.hue_deviate += model_random.jitter(0.1)

    def adjust_color(self, color):
        """Adjust rgba value to mutated hue and similarity range.
        pre: len(color.rgba) == 4
        """
        rgba = color.rgba
        dummy, lightness, saturation = colorsys.rgb_to_hls(
                                  rgba[0], rgba[1], rgba[2])
        hue = self._get_hue(color.base_diff_hue)
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        color.rgba = (rgb[0], rgb[1], rgb[2], rgba[3])

    def explain(self, formater):
        formater.text_item(_('Split complementary color scheme'))

    def copy(self):
        """The SplitComplementaryColorGamut copy constructor
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = SplitComplementaryColorGamut(self.get_trunk())
        new_one.hue = self.hue
        new_one.hue_deviate = self.hue_deviate
        return new_one

    def _get_hue(self, hue_dircetion):
        if hue_dircetion < 0:
            hue = model_random.cyclic_limit(self.hue - 0.5 + self.hue_deviate)
        elif hue_dircetion > 0:
            hue = model_random.cyclic_limit(self.hue + 0.5 + self.hue_deviate)
        else:
            hue = self.hue
        return hue
