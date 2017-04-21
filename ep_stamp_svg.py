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

from gettext import gettext as _

import random
import rsvg

import ka_debug
import model_random
import model_locus
import model_allele
import model_constraintpool
import ka_importer

STAMPREPEATER_CONSTRAINT = 'stamprepaeterconstraint'
THEME_CONSTRAINT = 'themeconstraint'

class SvgStamp(model_allele.Allele):
    """SvgStamp:.
    inv: self.max_states >= 0
    inv: len(ka_importer.get_svg_image_list(self.theme)) == len(self.mapping)
    inv: forall(self.mapping, lambda x: x >= 0 and x < len(ka_importer.get_svg_image_list(self.theme)))
    """

    cdef = [{'bind'  : STAMPREPEATER_CONSTRAINT,
             'name'  : 'Number of stamps used per location',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0, 'max': 3},
            {'bind'  : THEME_CONSTRAINT,
             'name'  : 'Permitted themes for stamps',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : ka_importer.get_theme_list()
            },
           ]

    def __init__(self, trunk, maxstates):
        """Constructor for a flip merger.
        pre: maxstates >= 0
        """
        super(SvgStamp, self).__init__(trunk)
        self.max_states = maxstates
        self.dw, self.dh = 1.0, 1.0
        self.theme = ''
        svg_image_list = ka_importer.get_svg_image_list(self.theme)
        self.mapping = [ix for ix in range(len(svg_image_list))]
        self.repeating = [1 for ix in range(self.max_states)]

    def __eq__(self, other):
        """Equality based on radius."""
        equal = isinstance(other, SvgStamp) \
                and self.max_states == other.max_states \
                and len(self.mapping) == len(other.mapping) \
                and len(self.repeating) == len(other.repeating) \
                and self.theme == other.theme
        if equal:
            for cix, value in enumerate(self.mapping):
                equal = equal and value == other.mapping[cix]
        if equal:
            for cix, value in enumerate(self.repeating):
                equal = equal and value == other.repeating[cix]
        return equal

    def randomize(self):
        """Randomize the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()

        self._randomize_mapping(cpool)
        number_of_repeaters_constraint = cpool.get(self, STAMPREPEATER_CONSTRAINT)
        min_r, max_r = number_of_repeaters_constraint[0], number_of_repeaters_constraint[1]
        self.repeating = [model_random.limit_range(ix, min_r, max_r)
                                            for ix in range(self.max_states)]
        random.shuffle(self.repeating)

    def _randomize_mapping(self, cpool):
        """
        pre: cpool is not None
        """
        full_theme_list = ka_importer.get_theme_list()
        theme_constraint = cpool.get(self, THEME_CONSTRAINT)
        theme_list = [th for th in full_theme_list if th in theme_constraint]
        self.theme = '' if len(theme_list) == 0 else random.choice(theme_list)
        svg_image_list = ka_importer.get_svg_image_list(self.theme)
        self.mapping = [ix for ix in range(len(svg_image_list))]
        random.shuffle(self.mapping)

    def mutate(self):
        """Make small random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()

        if model_random.is_mutating():
            self._randomize_mapping(cpool)

        if model_random.is_mutating():
            number_of_repeaters_constraint = cpool.get(self, STAMPREPEATER_CONSTRAINT)
            for rx, repeat in enumerate(self.repeating):
                self.repeating[rx] = model_random.jitter_discret_constrained(
                                        repeat, number_of_repeaters_constraint)

    def swap_places(self):
        """Shuffle mapping table."""
        if model_random.is_mutating():
            model_random.swap_places(self.mapping)
            svg_image_list = ka_importer.get_svg_image_list(self.theme)
            for dummy in range(len(svg_image_list) / 20):
                model_random.swap_places(self.mapping)
        if model_random.is_mutating():
            model_random.swap_places(self.repeating)

    def crossingover(self, other):
        """
        pre: isinstance(other, SvgStamp)
        pre: isinstance(self, SvgStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = SvgStamp(self.get_trunk(), self.max_states)
        self.dw, self.dh = 1.0, 1.0
        cross_sequence = model_random.crossing_sequence(2)
        if self.theme == other.theme:
            new_one.theme = self.theme[:]
            new_one.mapping = model_random.crossingover_nativeelement_list(
                                                            self.mapping,
                                                            other.mapping)
        else:
            if cross_sequence[0]:
                new_one.theme = other.theme[:]
                new_one.mapping = other.mapping[:]
            else:
                new_one.theme = self.theme[:]
                new_one.mapping = self.mapping[:]
        if self.max_states == other.max_states:
            new_one.max_states = self.max_states
            new_one.repeating = model_random.crossingover_nativeelement_list(
                                                        self.repeating,
                                                        other.repeating)
        return new_one
    
    def set_stamp_extent(self, dw, dh):
        """Set extent of stamp."""
        self.dw, self.dh = dw, dh

    def render(self, ctx, point, state):
        """
        pre: ctx is not None
        pre: len(point) == 2
        """
        svg_image_list = ka_importer.get_svg_image_list(self.theme)
        if len(svg_image_list) > 0:
            repeats = self.repeating[state % len(self.repeating)]
            for rx in range(repeats):
                svg_pathname = svg_image_list[self.mapping[
                                            (state + rx) % len(self.mapping)]
                                          % len(svg_image_list)]
                ctx.save()
#                ka_debug.matrix_s(ctx.get_matrix())
                svg = rsvg.Handle(file=svg_pathname)
                ctx.translate(-self.dw/2.0+point[0], -self.dh/2.0+point[1])
#                ka_debug.matrix(ctx.get_matrix())
                ctx.scale(self.dw/100.0, self.dh/100.0)
#                ka_debug.matrix(ctx.get_matrix())
                svg.render_cairo(ctx)
                svg.close()
#                ka_debug.matrix_r(ctx.get_matrix())
                ctx.restore()

    def explain(self):
        """
        post: len(__return__) == 3
        """
        return _('Theme is %s. Patterns are in SVG format: ') % self.theme, \
               None, \
               None

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, SvgStamp)
        # check for distinct references, needs to copy content, not references
        post: len(__return__.mapping) == len(self.mapping)
        post: __return__ is not self
        """
        new_one = SvgStamp(self.get_trunk(), self.max_states)
        new_one.dw, new_one.dh = self.dw, self.dh
        new_one.max_states = self.max_states
        new_one.theme = self.theme[:]
        new_one.mapping = [self.mapping[ix] for ix in range(len(self.mapping))]
        new_one.repeating = [self.repeating[ix] for ix in range(len(self.repeating))]
        return new_one
