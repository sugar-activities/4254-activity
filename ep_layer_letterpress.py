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

import sys
import traceback
import random
import pango
import pangocairo

import ka_debug
import model_layer
import model_random
import ka_factory
import model_locus
import model_constraintpool
import exon_color
import exon_position
import exon_buzzword

FONTFAMILY_CONSTRAINT  = 'fontfamilyconstraint'
FONTSTYLE_CONSTRAINT   = 'fontstyleconstraint'
FONTSIZE_CONSTRAINT   = 'fontsizeconstraint'
FONTWEIGHT_CONSTRAINT  = 'fontweightconstraint'
SAMPLERTYPE_CONSTRAINT = 'samplertypeconstraint'

class LetterPress(model_layer.Layer):
    """LetterPress
    """

    cdef = [{'bind'  : FONTFAMILY_CONSTRAINT,
             'name'  : 'Font family',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ['Normal',
                        'Sans',
                        'Serif',
                        'Monospace',]},
            {'bind'  : FONTSTYLE_CONSTRAINT,
             'name'  : 'Font style',
             'domain': model_constraintpool.INT_1_OF_N,
             'enum'  : [('Normal',  pango.STYLE_NORMAL),
                        ('Oblique', pango.STYLE_OBLIQUE),
                        ('Italic',  pango.STYLE_ITALIC),]},
            {'bind'  : FONTSIZE_CONSTRAINT,
             'name'  : 'Font size in percent of the drawing area.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 1, 'max': 100},
            {'bind'  : FONTWEIGHT_CONSTRAINT,
             'name'  : 'Specifies how bold or light the font should be.',
             'domain': model_constraintpool.INT_RANGE,
             'min'   : 100, 'max': 900},
            {'bind'  : SAMPLERTYPE_CONSTRAINT,
             'name'  : 'Permitted sampler types',
             'domain': model_constraintpool.STRING_1_OF_N,
             'enum'  : ka_factory.get_factory('sampler').keys()},
            ]

    font_style = {pango.STYLE_NORMAL:  'Normal', 
                  pango.STYLE_OBLIQUE: 'Oblique', 
                  pango.STYLE_ITALIC:  'Italic', 
                 }

    def __init__(self, trunk):
        """LetterPress diagram layer constructor"""
        super(LetterPress, self).__init__(trunk)
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.textcolor = exon_color.Color(self.path, 0, 0, 0, 1)
        self.family = cpool.get(self, FONTFAMILY_CONSTRAINT)[0]
        self.style = cpool.get(self, FONTSTYLE_CONSTRAINT)[0]
        self.size = cpool.get(self, FONTSIZE_CONSTRAINT)[0]
        self.weight = cpool.get(self, FONTWEIGHT_CONSTRAINT)[0]
        self.center = exon_position.Position(self.path, 0.0, 0.0)
        sampler_factory = ka_factory.get_factory('sampler')
        sampler_key = sampler_factory.keys()[0]
        self.sampler = sampler_factory.create(sampler_key, self.path)
        self.buzzwords = exon_buzzword.Buzzword(self.path, [''])

    def dot(self):
        result = ""
        anchor = ka_debug.dot_id(self) + ' -> '
        for ref in [self.textcolor, self.center, self.sampler, self.buzzwords]:
            result += ka_debug.dot_ref(anchor, ref)
        return result
    
    def __eq__(self, other):
        """Equality based on the objects components."""
        equal = isinstance(other, LetterPress) \
                and super(LetterPress, self).__eq__(other) \
                and self.textcolor == other.textcolor \
                and self.family == other.family \
                and self.style == other.style \
                and self.size == other.size \
                and self.weight == other.weight \
                and self.center == other.center \
                and self.sampler == other.sampler \
                and self.buzzwords == other.buzzwords
        return equal

    def randomize(self):
        """Randomize the layers components."""
        super(LetterPress, self).randomize()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.textcolor.randomize()
        family_constraint = cpool.get(self, FONTFAMILY_CONSTRAINT)
        self.family = random.choice(family_constraint)
        style_constraint = cpool.get(self, FONTSTYLE_CONSTRAINT)
        self.style = random.choice(style_constraint)
        size_constraint = cpool.get(self, FONTSIZE_CONSTRAINT)
        self.size = model_random.randint_constrained(size_constraint)
        weight_constraint = cpool.get(self, FONTWEIGHT_CONSTRAINT)
        self.weight = model_random.randint_constrained(weight_constraint)
        self.center.randomize()

        sampler_factory = ka_factory.get_factory('sampler')
        samplertype_constraint = cpool.get(self, SAMPLERTYPE_CONSTRAINT)
        self.sampler = sampler_factory.create_random(samplertype_constraint, 
                                                     self.path)
        self.sampler.randomize()

        self.buzzwords.randomize()

    def mutate(self):
        """Make small random changes to the layers components."""
        super(LetterPress, self).mutate()
        cpool = model_constraintpool.ConstraintPool.get_pool()
        self.textcolor.mutate()
        if model_random.is_mutating():
            family_constraint = cpool.get(self, FONTFAMILY_CONSTRAINT)
            self.family = random.choice(family_constraint)
        if model_random.is_mutating():
            style_constraint = cpool.get(self, FONTSTYLE_CONSTRAINT)
            self.style = random.choice(style_constraint)
        if model_random.is_mutating():
            size_constraint = cpool.get(self, FONTSIZE_CONSTRAINT)
            self.size = model_random.jitter_discret_constrained(
                                                    self.size, size_constraint)
        if model_random.is_mutating():
            weight_constraint = cpool.get(self, FONTWEIGHT_CONSTRAINT)
            self.weight = model_random.jitter_discret_constrained(
                                                self.weight, weight_constraint)
        self.center.mutate()
        self.sampler.mutate()
        self.buzzwords.mutate()

    def swap_places(self):
        """Shuffle similar components."""
        self.center.swap_places()
        self.sampler.swap_places()
        self.buzzwords.swap_places()

    def crossingover(self, other):
        """
        pre: isinstance(other, LetterPress)
        pre: isinstance(self, LetterPress)
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        post: __return__ is not other
        post: model_locus.unique_check(__return__, self, other) == ''
        """
        new_one = LetterPress(self.get_trunk())
        crossing = self.crossingover_base(new_one, other, 7)
        new_one.textcolor = self.textcolor.crossingover(other.textcolor)
        new_one.center = self.center.crossingover(other.center)
        new_one.sampler = model_random.crossingover_elem(self.sampler,
                                                      other.sampler)
        new_one.buzzwords = self.buzzwords.crossingover(other.buzzwords)
        new_one.family = self.family if crossing[3] else other.family
        new_one.style = self.style if crossing[4] else other.style
        new_one.size = self.size if crossing[5] else other.size
        new_one.weight = self.weight if crossing[6] else other.weight
        return new_one

    def render(self, task, ctx, width, height):
        """
        pre: ctx is not None
        pre: width > 0
        pre: height > 0
        pre: width == height
        """
        self.begin_render(ctx, width, height)
 
        ctx.save()
#        ka_debug.matrix_s(ctx.get_matrix())
        ctx.scale(1.0/width, 1.0/height)
#        ka_debug.matrix(ctx.get_matrix())
        pango_ctx = pangocairo.CairoContext(ctx)
        points = self.sampler.get_sample_points()
        if len(points) > 0:
            fi = di = -1
            for word in self.buzzwords.wordlist:
                di = (di+1) % len(points)
                px = self.center.x_pos + points[di][0]
                py = self.center.y_pos + points[di][1]
    
                try:
                    layout = pango_ctx.create_layout()
                    fi = (fi+1) % len(self.family)
                    desc = pango.FontDescription(self.family[fi])
                    desc.set_size(int(self.size * width * 0.01 * pango.SCALE))
                    desc.set_style(self.style)
                    desc.set_weight(self.weight)
                    layout.set_text(word.encode('utf-8'))
                    layout.set_font_description(desc)
                    layout.set_alignment(pango.ALIGN_CENTER)
                    rgba = self.textcolor.rgba
                    pango_ctx.set_source_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
                    pango_ctx.update_layout(layout)
        
                    pixel_size = layout.get_pixel_size()
                    dx, dy = 0.5 * pixel_size[0], 0.9 * pixel_size[1]
                    pango_ctx.move_to((width * px) - dx, (height * py) - dy)
                    pango_ctx.show_layout(layout)
                except:
                    ka_debug.err('failed on pango [%s] [%s]' % \
                           (sys.exc_info()[0], sys.exc_info()[1]))
                    traceback.print_exc(file=sys.__stderr__)
#        ka_debug.matrix_r(ctx.get_matrix())
        ctx.restore()

    def explain(self, formater):
        formater.begin_list(_('Layer ') + self.__class__.__name__)
        super(LetterPress, self).explain(formater)
        formater.text_list(_('buzzwords: '), self.buzzwords.wordlist)
        formater.color_item(self.textcolor, _('text color:'))
        formater.text_item(_('Font: ') + self.family
                            + ', ' + LetterPress.font_style[self.style]
                            + ', ' + str(self.size)
                            + ', ' + str(self.weight))
        formater.position_item(self.center, _('center:'))
        text, surface, descr = self.sampler.explain()
        if surface is not None:
            formater.surface_item(surface, _('sampling points: ') + text, descr)
        else:
            formater.text_item(text)
        formater.end_list()

    def copy(self):
        """The LetterPress diagram layers copy constructor.
        # check for distinct references, needs to copy content, not references
        post: __return__ is not self
        """
        new_one = LetterPress(self.get_trunk())
        self.copy_base(new_one)
        new_one.textcolor = self.textcolor.copy()
        new_one.family = self.family
        new_one.style = self.style
        new_one.size = self.size
        new_one.weight = self.weight
        new_one.center = self.center.copy()
        new_one.sampler = self.sampler.copy()
        new_one.buzzwords = self.buzzwords.copy()
        return new_one
