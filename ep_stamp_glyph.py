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

import unicodedata
import random
import cairo
import model_random
import model_locus
import model_allele
import model_constraintpool
from gettext import gettext as _

GLYPHFONTSIZE_CONSTRAINT = 'glyphfontsizeconstraint'
GLYPHFONTFAMILY_CONSTRAINT  = 'glyphfontfamilyconstraint'
GLYPHCATEGORY_CONSTRAINT = 'glyphcategoryconstraint'

_unichar_category = None

unichrtab = (
    0x00a4,
    0x00ac,
    0x00b1,
    0x00b5,
    0x00b6,
    0x00bc,
    0x00bd,
    0x00be,
    0x00c6,
    0x00d8,
    0x00e6,
    0x00f8,
    0x013d,
    0x013f,
    0x0152,
    0x0153,
    0x0192,
    0x0402,
    0x0409,
    0x040a,
    0x0428,
    0x0429,
    0x042d,
    0x042e,
    0x0431,
    0x0444,
    0x044d,
    0x044e,
    0x0459,
    0x0498,
    0x04b4,
    0x04be,
    0x04c1,
    0x04d4,
    0x04d5,
    0x04da,
    0x04dc,
    0x04de,
    0x04f4,
    0x2021,
    0x2202,
    0x2206,
    0x2211,
    0x221a,
    0x221e,
    0x2260,
)

def classify_unichrtab():
    global _unichar_category
    if _unichar_category is None:
        _unichar_category = set([])
        for ux in range(len(unichrtab)):
            uc = unichr(unichrtab[ux])
#            print uc, '%04x' % ord(uc), unicodedata.category(uc), unicodedata.name(uc, '')
            _unichar_category.add(unicodedata.category(uc))
#        print 'unichar_category', type(_unichar_category), _unichar_category
    return _unichar_category

def select_by(category_list):
    selected = []
    for ux in range(len(unichrtab)):
        uc = unichr(unichrtab[ux])
        if unicodedata.category(uc) in category_list:
            selected.append(uc)
#    print 'select_by', selected, category_list
    return selected

class GlyphStamp(model_allele.Allele):
    """GlyphStamp:.
    inv: self.size >= 0.0
    """

    cdef = [{'bind'  : GLYPHFONTSIZE_CONSTRAINT,
             'name'  : 'Font size in percent of the drawing area.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 0.01, 'max': 1.0},
            {'bind'  : GLYPHFONTFAMILY_CONSTRAINT,
             'name'  : 'Font family',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ['Normal',
                        'Sans',
                        'Serif',
                        'Monospace',]},
            {'bind'  : GLYPHCATEGORY_CONSTRAINT,
             'name'  : 'Permitted themes for stamps',
             'domain': model_constraintpool.STRING_M_OF_N,
             'enum'  : classify_unichrtab()
            },
           ]

    def __init__(self, trunk, maxstates):
        """Constructor for a flip merger."""
        super(GlyphStamp, self).__init__(trunk)
        self.max_states = maxstates
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.size = cpool.get(self, GLYPHFONTSIZE_CONSTRAINT)[0]
        self.family = cpool.get(self, GLYPHFONTFAMILY_CONSTRAINT)[0]
        self.category_list = ['Sm']
        self.unichr_list = select_by(self.category_list)
        self.mapping = [ix for ix in range(len(self.unichr_list))]


    def __eq__(self, other):
        """Equality"""
        equal = isinstance(other, GlyphStamp) \
                and self.max_states == other.max_states \
                and len(self.mapping) == len(other.mapping) \
                and len(self.category_list) == len(other.category_list) \
                and self.size == other.size \
                and self.family == other.family
        if equal:
            for cix, value in enumerate(self.mapping):
                equal = equal and value == other.mapping[cix]
        if equal:
            for cix, value in enumerate(self.category_list):
                equal = equal and value == other.category_list[cix]
        return equal

    def randomize(self):
        """Randomize the stamps components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        random.shuffle(self.mapping)
        size_constraint = cpool.get(self, GLYPHFONTSIZE_CONSTRAINT)
        self.size = model_random.uniform_constrained(size_constraint)
        family_constraint = cpool.get(self, GLYPHFONTFAMILY_CONSTRAINT)
        self.family = random.choice(family_constraint)
        self._randomize_mapping(cpool)

    def _randomize_mapping(self, cpool):
        """
        pre: cpool is not None
        """
        category_constraint = cpool.get(self, GLYPHCATEGORY_CONSTRAINT)
        self.category_list = [ca for ca in classify_unichrtab() if ca in category_constraint]
        self.unichr_list = select_by(self.category_list)
        self.mapping = [ix for ix in range(len(self.unichr_list))]
        random.shuffle(self.mapping)

    def mutate(self):
        """Make small random changes to the layers components."""
        cpool = model_constraintpool.ConstraintPool.get_pool()
        if model_random.is_mutating():
            self._randomize_mapping(cpool)

        size_constraint = cpool.get(self, GLYPHFONTSIZE_CONSTRAINT)
        self.size = model_random.jitter_constrained(self.size, size_constraint)
        if model_random.is_mutating():
            family_constraint = cpool.get(self, GLYPHFONTFAMILY_CONSTRAINT)
            self.family = random.choice(family_constraint)

    def swap_places(self):
        """Shuffle mapping table."""
        model_random.swap_places(self.mapping)

    def crossingover(self, other):
        """
        pre: isinstance(other, GlyphStamp)
        pre: isinstance(self, GlyphStamp)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = GlyphStamp(self.get_trunk(), self.max_states)
        cross_sequence = model_random.crossing_sequence(3)
        new_one.size = other.size if cross_sequence[0] else self.size
        new_one.family = self.family if cross_sequence[1] else other.family
        if cross_sequence[2]:
            new_one.category_list = other.category_list[:]
            new_one.unichr_list = other.unichr_list[:]
            new_one.mapping = other.mapping[:]
        else:
            new_one.category_list = self.category_list[:]
            new_one.unichr_list = self.unichr_list[:]
            new_one.mapping = self.mapping[:]
        return new_one
    
    def set_stamp_extent(self, width, height):
        """Set extent of stamp. This stamps will ignore these parameters."""
        pass

    def render(self, ctx, point, state):
        """
        pre: ctx is not None
        pre: len(point) == 2
        """
        uc = self.unichr_list[self.mapping[state % len(self.mapping)] % len(self.unichr_list)]
        ctx.select_font_face(self.family,
                             cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.size)
        x_bearing, y_bearing, width, height = ctx.text_extents(uc)[:4]
        ctx.move_to(point[0] - width / 2 - x_bearing,
                    point[1] - height / 2 - y_bearing)
        ctx.show_text(uc)

    def explain(self):
        """
        post: len(__return__) == 3
        """
        text = _('Font: ') + self.family + ', ' + unicode(self.size) + ', ' + \
            _('A collection of characters from category : ') + \
            unicode(self.category_list)
        return text, \
               None, \
               None

    def copy(self):
        """A copy constructor.
        post: isinstance(__return__, GlyphStamp)
        # check for distinct references, needs to copy content, not references
        post: len(__return__.mapping) == len(self.mapping)
        post: __return__ is not self
        """
        new_one = GlyphStamp(self.get_trunk(), self.max_states)
        new_one.size = self.size
        new_one.family = self.family
        new_one.category_list = self.category_list[:]
        new_one.unichr_list = self.unichr_list[:]
        new_one.mapping = self.mapping[:]
        return new_one

